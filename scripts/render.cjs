// Render scene.html frame-by-frame with Playwright and encode with ffmpeg.
//   node scripts/render.cjs                 → out/guess-mobys-game-10s.mp4
//   node scripts/render.cjs --stills 0.9,2.6 → out/stills/*.png (quick previews)
const path = require('path');
const fs = require('fs');
const { spawn, execFileSync } = require('child_process');
let playwright;
try { playwright = require('playwright'); } catch { playwright = require('/opt/node22/lib/node_modules/playwright'); }

const ROOT = path.resolve(__dirname, '..');
const FFMPEG = process.env.FFMPEG ||
  execFileSync('python3', ['-c', 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())']).toString().trim();
const OUT = path.join(ROOT, 'out', 'guess-mobys-game-10s.mp4');

(async () => {
  const stillsArg = process.argv.indexOf('--stills');
  const browser = await playwright.chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1000 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto('file://' + path.join(ROOT, 'scene.html'));
  await page.evaluate(() => window.ready);
  const stage = await page.$('#stage');

  if (stillsArg > -1) {
    const dir = path.join(ROOT, 'out', 'stills');
    fs.mkdirSync(dir, { recursive: true });
    for (const s of process.argv[stillsArg + 1].split(',').map(Number)) {
      await page.evaluate(t => window.renderAt(t), s);
      await stage.screenshot({ path: path.join(dir, `t${s.toFixed(2)}.png`) });
    }
    await browser.close();
    return;
  }

  const { DUR, FPS } = await page.evaluate(() => ({ DUR: window.DUR, FPS: window.FPS }));
  const total = Math.round(DUR * FPS);
  const src = path.join(ROOT, 'assets', 'moby-thinking.mp4');
  // Moby's audio follows the same retime as the picture (0.3–4.0s stretched to 3.9s, then 4.0–5.02s).
  const ff = spawn(FFMPEG, [
    '-loglevel', 'error', '-y',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', src,
    '-filter_complex',
    '[1:a]atrim=0.3:4.0,asetpts=PTS-STARTPTS,atempo=0.9487[a1];' +
    '[1:a]atrim=4.0:5.02,asetpts=PTS-STARTPTS[a2];' +
    '[a1][a2]concat=n=2:v=0:a=1,afade=t=in:d=0.15,afade=t=out:st=4.7:d=0.22,apad=whole_dur=10[a]',
    '-map', '0:v', '-map', '[a]',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    '-c:a', 'aac', '-b:a', '160k', '-t', String(DUR),
    OUT,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  for (let i = 0; i < total; i++) {
    await page.evaluate(t => window.renderAt(t), i / FPS);
    const buf = await stage.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`frame ${i}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg exit ' + c)))));
  await browser.close();
  console.log('wrote', OUT);
})().catch(e => { console.error(e); process.exit(1); });

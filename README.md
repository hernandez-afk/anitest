# Guess Moby's Game spot

Two cuts, both 1500×1000, 60fps, H.264, no audio:

- `out/guess-mobys-game-v1.mp4` (12s): the answer is typed into a guess bar beside Moby.
- `out/guess-mobys-game-alt2.mp4` (13.6s): the guess is typed on the in-game keyboard over a blurred screenshot clue.

| Time | Version 1 | Alt 2 |
|------|-----------|-------|
| 0–6s | Moby thinks. "Hmm… what game was that?" types into the guess bubble, then the clue chips arrive one at a time: *Specific frame… / Released in… / That iconic detail…* | Same |
| 6–9s (v1) / 6–10.6s (alt2) | **WAIT… I GOT IT!** Moby lights up. *Adventure* is typed into the guess bar, Guess is pressed, then a "Pixel Perfect" badge and confetti | **WAIT… I GOT IT!**, then the Play screen slides in. *Adventure* is typed key by key on the in-game keyboard over a blurred frame; Guess brings the frame into focus and the badge lands |
| last 3s | Flash cut to the end card: the logo, then *4 clues. 1 game. Can you guess it?* | Same |

The Adventure frame in Alt 2 is a drawn stand-in for the gold-castle room. Put a real screenshot at
`assets/adventure.png` and re-render to use it instead.

Moby on his own: `out/moby-thinking-solving.gif` (415×640, transparent background, loops, about 5.8s including a 1s hold on the solved pose). Rebuild it with `python3 scripts/make_gif.py`.

A web-sized copy: `out/moby-thinking-solving-128kb.gif` (156×240, about 8fps, 47 colours, 97KB, about 4.8s with one second of the thinking hold cut). It needs [gifsicle](https://www.lcdf.org/gifsicle/):
`python3 scripts/make_gif.py --height 240 --step 3 --colours 47 --lossy 40 --cut 73-96 --out out/moby-thinking-solving-128kb.gif`

| Time | Beat |
|------|------|
| 0–4s | Moby thinks. A guess-bubble thought ("Hmm… what game was that?") types itself in, and the clue chips flash in: *Specific frame… / Released in… / That iconic detail…* |
| 4–7s | Moby blinks and lights up (glow + rays): **WAIT… I GOT IT!** The answer is typed into the guess bar, Guess is pressed, then a "Pixel Perfect" confirmation and confetti |
| 7–10s | Flash cut to a centred end card: the logo, then *4 clues. 1 game. Can you guess it?* |

The bubbles, chips, keys and buttons use the mobile keyboard styles (`.kb-*`) and mode-1 tokens from
[hernandez-afk/gmg](https://github.com/hernandez-afk/gmg). Type is Fugaz One and Work Sans.

## Rebuild

```sh
pip install imageio-ffmpeg pillow numpy scipy
bash scripts/prep.sh          # extracts frames and keys Moby off his white background
node scripts/render.cjs                  # Version 1 → out/guess-mobys-game-v1.mp4
node scripts/render.cjs --variant alt2   # Alt 2     → out/guess-mobys-game-alt2.mp4
node scripts/render.cjs --variant alt2 --stills 1,6.5,9.8   # quick preview PNGs
```

To change the copy or the answer, edit the constants at the top of the `<script>` in `scene.html`.
`HOOK` sets how long the opening lasts; everything after it moves with it. Moby's thinking fills the
hook by repeating source frames 73–96, a one-second idle loop that joins seamlessly (see `clipFrame()`).

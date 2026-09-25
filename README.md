# Guess Moby's Game: 10-second spot

Final render: `out/guess-mobys-game-10s.mp4` (1500×1000, 60fps, 10s, H.264, no audio)

Moby on his own: `out/moby-thinking-solving.gif` (415×640, transparent background, loops, about 5.8s including a 1s hold on the solved pose). Rebuild it with `python3 scripts/make_gif.py`.

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
node scripts/render.cjs       # renders scene.html frame by frame, then encodes with ffmpeg
node scripts/render.cjs --stills 1,2.5,6   # quick preview PNGs
```

To change the copy or the answer, edit the constants at the top of the `<script>` in `scene.html`.
The Moby clip is retimed in `clipTime()`: its thinking beat (0.3–4.0s) is stretched over 0–3.9s, then the realization (4.0–5.02s) plays at normal speed.

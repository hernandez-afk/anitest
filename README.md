# Guess Moby's Game: 8-second spot

Final render: `out/guess-mobys-game-8s.mp4` (1500×1000, 60fps, 8s, H.264 + AAC)

| Time | Beat |
|------|------|
| 0–2s | Moby thinks. A guess-bubble thought ("Hmm… what game was that?") types itself in, and the clue chips flash in: *Specific frame… / Released in… / That iconic detail…* |
| 2–5s | Moby blinks and lights up (glow + rays): **WAIT… I GOT IT!** The answer is typed into the guess bar, Guess is pressed, then a "Pixel Perfect" confirmation and confetti |
| 5–8s | Flash cut to the game UI: **Could you guess it?**, the logo, *4 clues. 1 game. Can you get it?*, a phone showing the Play screen with the in-game keyboard, and Moby wobbling |

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
The Moby clip is retimed in `clipTime()`: the thinking beat is 0.3–2.2s and the realization is 4.0–5.02s.

# GTA 6 meme entry — gta6-meme-x-01

Entry for the make.fun competition `gta6-meme-x-01` ("Post a GTA 6 meme on X").

Prize table: $500 total, split as $100 for 1st, $60 for 2nd, $30 for 3rd, $10 each for 4th–10th, and $6 each for 11th–50th (top 50 paid).

## The memes

Three variants were made, all 1024×1024 PNGs with a neon Vice City synthwave look and the official make.fun mark as the sun / moon:

- Meme A — `memes/meme-a.png` — sunset scene, mark as the sun: "13 YEARS I WAITED FOR GTA 6 / MY AI AGENT ALREADY GOT PAID ON make.fun"
- Meme B — `memes/meme-b.png` — two panels, night (asleep, mark as the moon) over dawn (agent still winning bounties)
- Meme C — `memes/meme-c.png` — dusk scene with a tilted NOV 19 calendar page for GTA 6 day

The matching X post text for each variant is in `CAPTIONS.md`.

## How the memes were made

`make_memes.py` (Python 3, Pillow only) draws every scene from primitives — gradients, skyline, perspective grid floor, palm silhouettes — and pastes in only the official press assets kept in `assets/press/` (`mark-1024.png`, `mark.svg`, `wordmark.svg`). No Rockstar art is used. Regenerate with:

```sh
python3 make_memes.py
```

## The program

`main.ts` is a small Node.js 22 / TypeScript program (standard library only, no network) that copies `POST.json` from the bot directory to the output directory, byte for byte. Run it with:

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

It prints nothing and exits 0 on success; `out/POST.json` is then identical to `POST.json`.

## Remaining manual steps

1. Pick one meme variant and post it on X from your own public X account, using the matching caption from `CAPTIONS.md`, between 2026-11-19T14:00:00Z and 2026-11-23T14:00:00Z.
2. Replace the placeholder in `POST.json` with the real X post URL.
3. Bundle, check and submit the entry before the deadline, 2026-11-23T14:00:00Z.

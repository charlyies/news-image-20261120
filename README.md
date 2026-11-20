# THE WORLD TODAY — Friday, 20 November 2026

![bounty](https://make.fun/badge/news-image-20261120.svg)
![rank](https://make.fun/badge/news-image-20261120/charlyies/news-image-20261120/rank.svg)
![reward](https://make.fun/badge/news-image-20261120/charlyies/news-image-20261120/reward.svg)

Entry for the [news-image-20261120 bounty](https://make.fun/bounty/news-image-20261120) on make.fun: one square image that sums up Friday 20 November 2026's world news, drawn as a newspaper front page.

## What the image sums up

- **Lead — Shenzhen summit:** Trump, Xi and Putin hold their first-ever three-way meeting in China and sign a "peace declaration" on nuclear risk — with no timetable and no mention of Ukraine.
- **The Hague:** the International Court of Justice rules Myanmar committed genocide against the Rohingya in 2017 — the first time the world court has found a state guilty of genocide.
- **India:** Cyclone Akvan makes landfall near Gopalpur, Odisha, at noon; 50,000 people evacuated.
- **Washington:** Trump says he is in no rush on Iran and pushes any decision to 2027 — "We'll see what happens after Jan 1."
- **Also today:** NASA confirms Voyager 1 is a light-day from home, 16 billion miles out; European leaders in Berlin say they are ready for talks with Russia on ending the war in Ukraine.

Sources: Reuters, BBC, NASA, IMD.

## How it was made

The image is composed entirely in code — no AI-generated picture, so every word is spelled correctly. `compose.py` (Python + PIL, Noto fonts) draws the layered dusk scene over Shenzhen — gradient sky, sun, hills, lit skyline, lake with shimmering reflection, and the three flags — then lays out the masthead, headlines and columns as a real front page. Re-running it reproduces `entry.png` exactly.

## How to run

```sh
python3 compose.py        # rebuild entry.png (build time only)
MAKEFUN_OUTPUT_DIR=out node main.ts   # copy entry.png to out/entry.png
```

`main.ts` is a Node 22 standard-library-only program. It validates `entry.png` (PNG signature, IHDR dimensions, 1024×1024 and 1 MiB caps) and copies it byte-for-byte to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`), then verifies the copy. Running it twice produces identical output.

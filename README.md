# Saturday 21 November 2026 — the world in one page

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/c/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/flamsx/news-image-20261121/rank.svg)](https://make.fun/c/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/flamsx/news-image-20261121/reward.svg)](https://make.fun/c/news-image-20261121)

One image that sums up the world's news of **Saturday 21 November 2026**:
Riyadh intercepts three Houthi missiles, COP31 runs into overtime in Antalya,
and BepiColombo reaches Mercury after eight years — 37 stories across 6 continents,
every one dated, every card sourced.

## How it is built

`draw.py` draws the 1024×1024 front page with the Lexend font (OFL, in `fonts/`)
and saves it as `entry.png`. `main.py` copies `entry.png` to the output directory.
The render is deterministic: two runs produce byte-identical output.

```sh
python3 draw.py entry.png
python3 main.py
```

## Sources

Reuters, AP, BBC, ATP, ESA, JAXA, EU, Kyiv Independent, IANS, and other wires,
checked on 21 November 2026. Stories first reported on an earlier day are listed
in the DATE CHECK box on the page, not shown as Saturday's news.

Entry for the [news-image-20261121](https://make.fun/c/news-image-20261121) competition on make.fun.

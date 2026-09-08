"""Day 20 sea chart: render the assembled image with its sea monsters marked.

Not a day module -- bench.py and pytest ignore it.  Runs the day 20 solver on
the real input and on the statement's nine-tile example, marks every cell a
sea monster covers with `O`, and writes one self-contained HTML page showing
the 96x96 image in the orientation where the monsters appear, a draggable
24x24 zoom window, and the 24x24 example.  Water, rough water and monster
cells are three colours; hovering the zoom names a cell.

    python python/day20_chart.py                  # -> inputs/day20_sea_chart.html
    python python/day20_chart.py somewhere.html   # -> that path

The default output sits under inputs/ because the picture is derived from
the puzzle input, which is gitignored on request of Advent of Code.

Everything on the page comes from day20.py: the assembly, the stitch, the
monster search.  The script checks, before writing, that the `#` cells left
after marking number exactly the part 2 answer, on both images.
"""

import json
import re
import sys
from pathlib import Path

import day20

REPO = Path(__file__).resolve().parent.parent
STATEMENT = REPO / "Problem_Statements" / "days" / "day20.md"
DEFAULT_OUT = REPO / "inputs" / "day20_sea_chart.html"


def sample_tiles() -> day20.Tiles:
    """The statement's nine example tiles, read from the statement file."""
    text = STATEMENT.read_text(encoding="utf-8-sig")
    match = re.search(r"```text\n(Tile 2311:.*?)```", text, re.S)
    if match is None:
        raise SystemExit(f"could not find the example tiles in {STATEMENT}")
    return day20.parse_input(match.group(1))


def marked_image(tiles: day20.Tiles) -> tuple[list[str], int, int]:
    """The stitched image in its monster orientation with covered cells as `O`.

    Returns (rows, monsters, remaining_hashes).  Raises if monsters appear in
    more or fewer than one orientation, which the tests say never happens.
    """
    image = day20.stitch(day20.assemble(tiles))
    views = [view for view in day20.orientations(image) if day20.monster_anchors(view)]
    if len(views) != 1:
        raise SystemExit(f"monsters appear in {len(views)} orientations, expected 1")
    view = views[0]
    covered = day20.monster_cells(view)
    rows = [
        "".join("O" if (r, c) in covered else ch for c, ch in enumerate(row)) for r, row in enumerate(view)
    ]
    remaining = sum(row.count("#") for row in rows)
    if remaining != day20.roughness(image):
        raise SystemExit("marked image disagrees with part 2")
    return rows, len(day20.monster_anchors(view)), remaining


def render(real: list[str], sample: list[str], stats: dict[str, int]) -> str:
    page = TEMPLATE
    for key, value in stats.items():
        page = page.replace(f"__{key}__", f"{value:,}")
    return page.replace("__REAL__", json.dumps(real)).replace("__SAMPLE__", json.dumps(sample))


def main(argv: list[str] | None = None) -> int:
    out = Path(argv[0]) if argv else DEFAULT_OUT
    real_tiles = day20.parse_input(day20.INPUT.read_text())
    real, monsters, roughness = marked_image(real_tiles)
    sample, sample_monsters, sample_roughness = marked_image(sample_tiles())
    stats = {
        "SIDE": len(real),
        "CELLS": len(real) * len(real[0]),
        "HASHES": roughness + monsters * len(day20.MONSTER_CELLS),
        "MONSTERS": monsters,
        "COVERED": monsters * len(day20.MONSTER_CELLS),
        "ROUGHNESS": roughness,
        "SAMPLE_MONSTERS": sample_monsters,
        "SAMPLE_HASHES": sample_roughness + sample_monsters * len(day20.MONSTER_CELLS),
        "SAMPLE_ROUGHNESS": sample_roughness,
    }
    out.write_text(render(real, sample, stats), encoding="utf-8", newline="\n")
    print(f"wrote {out} ({monsters} monsters, roughness {roughness})")
    return 0


TEMPLATE = """\
<title>Jurassic Jigsaw Sea Chart</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
  :root {
    --ground: #EEF3F5;
    --panel: #FFFFFF;
    --line: #C9D7DD;
    --ink: #12303D;
    --muted: #5E7681;
    --water: #DDE9EE;
    --hash: #12303D;
    --monster: #E85D3A;
    --window: #E85D3A;
    color-scheme: light;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --ground: #081820;
      --panel: #0F2933;
      --line: #1F4351;
      --ink: #E8EEF1;
      --muted: #8FA9B5;
      --water: #0B1F2A;
      --hash: #E8EEF1;
      --monster: #FF7A59;
      --window: #FF7A59;
      color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --ground: #081820;
    --panel: #0F2933;
    --line: #1F4351;
    --ink: #E8EEF1;
    --muted: #8FA9B5;
    --water: #0B1F2A;
    --hash: #E8EEF1;
    --monster: #FF7A59;
    --window: #FF7A59;
    color-scheme: dark;
  }
  body {
    background: var(--ground);
    color: var(--ink);
    font-family: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
    font-size: 15px;
    line-height: 1.5;
  }
  main { max-width: 1120px; margin: 0 auto; padding: 32px 24px 48px; }
  header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 24px; margin-bottom: 20px; }
  h1 { font-size: 26px; font-weight: 600; margin: 0; letter-spacing: -0.01em; text-wrap: balance; }
  h2 { font-size: 13px; font-weight: 500; margin: 0 0 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }
  .lede { color: var(--muted); margin: 0; max-width: 62ch; }
  .legend { display: flex; flex-wrap: wrap; gap: 8px 22px; margin: 0 0 20px; padding: 0; list-style: none; font-family: "IBM Plex Mono", Consolas, monospace; font-size: 13px; }
  .legend li { display: flex; align-items: center; gap: 8px; }
  .swatch { width: 14px; height: 14px; border: 1px solid var(--line); }
  .grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 24px; align-items: start; }
  @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } }
  .panel { background: var(--panel); border: 1px solid var(--line); padding: 16px; }
  .frame { overflow-x: auto; }
  canvas { display: block; image-rendering: pixelated; image-rendering: crisp-edges; max-width: 100%; height: auto; touch-action: none; }
  #overview { cursor: grab; }
  #overview.dragging { cursor: grabbing; }
  .readout { font-family: "IBM Plex Mono", Consolas, monospace; font-size: 13px; color: var(--muted); margin: 10px 0 0; font-variant-numeric: tabular-nums; }
  .readout b { color: var(--ink); font-weight: 500; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px 20px; margin: 24px 0 28px; padding: 16px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
  .stat { font-family: "IBM Plex Mono", Consolas, monospace; font-variant-numeric: tabular-nums; }
  .stat .n { font-size: 20px; font-weight: 500; display: block; }
  .stat .l { font-size: 12px; color: var(--muted); }
  .example { margin-top: 28px; }
  .example .lede { margin-bottom: 12px; }
  .note { color: var(--muted); font-size: 13px; margin: 10px 0 0; }
</style>

<main>
  <header>
    <h1>Jurassic Jigsaw Sea Chart</h1>
    <p class="lede">The __SIDE__×__SIDE__ image from the assembled tiles, shown in the one orientation where sea monsters appear. Drag the window on the overview to zoom into any section.</p>
  </header>

  <ul class="legend">
    <li><span class="swatch" style="background: var(--water)"></span><span>. water</span></li>
    <li><span class="swatch" style="background: var(--hash)"></span><span># rough water</span></li>
    <li><span class="swatch" style="background: var(--monster)"></span><span>O sea monster</span></li>
  </ul>

  <div class="grid">
    <section class="panel">
      <h2>Overview · __SIDE__ × __SIDE__</h2>
      <div class="frame"><canvas id="overview" width="480" height="480" aria-label="Full image with sea monsters marked"></canvas></div>
      <p class="readout" id="overview-readout">window at row <b>0</b>, col <b>0</b></p>
    </section>
    <section class="panel">
      <h2>Section · 24 × 24</h2>
      <div class="frame"><canvas id="detail" width="480" height="480" aria-label="Zoomed 24 by 24 section of the image"></canvas></div>
      <p class="readout" id="detail-readout">hover a cell</p>
    </section>
  </div>

  <div class="stats">
    <div class="stat"><span class="n">__CELLS__</span><span class="l">cells</span></div>
    <div class="stat"><span class="n">__HASHES__</span><span class="l"># cells</span></div>
    <div class="stat"><span class="n">__MONSTERS__</span><span class="l">sea monsters</span></div>
    <div class="stat"><span class="n">__COVERED__</span><span class="l">cells they cover</span></div>
    <div class="stat"><span class="n">__ROUGHNESS__</span><span class="l">roughness (part 2)</span></div>
  </div>

  <section class="example">
    <h2>The statement's example · 24 × 24</h2>
    <p class="lede">The nine-tile sample assembled, borders stripped, and turned to the orientation with monsters: __SAMPLE_MONSTERS__ of them, __SAMPLE_HASHES__ # cells, roughness __SAMPLE_ROUGHNESS__.</p>
    <div class="panel" style="display: inline-block">
      <div class="frame"><canvas id="example" width="480" height="480" aria-label="The statement's 24 by 24 example image with sea monsters marked"></canvas></div>
    </div>
    <p class="note">Every cell here comes from python/day20.py: the assembly, the stitch, and the monster search. The O cells are exactly the ones subtracted for part 2. Generated by python/day20_chart.py.</p>
  </section>
</main>

<script>
  const REAL = __REAL__;
  const SAMPLE = __SAMPLE__;
  const WIN = 24;

  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const colors = () => ({ ".": css("--water"), "#": css("--hash"), "O": css("--monster"), window: css("--window") });

  function paint(canvas, rows, r0, c0, size, cell, pal) {
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        ctx.fillStyle = pal[rows[r0 + r][c0 + c]];
        ctx.fillRect(c * cell, r * cell, cell, cell);
      }
    }
  }

  const overview = document.getElementById("overview");
  const detail = document.getElementById("detail");
  const example = document.getElementById("example");
  const overviewReadout = document.getElementById("overview-readout");
  const detailReadout = document.getElementById("detail-readout");
  const N = REAL.length;
  const OV = overview.width / N;
  const DT = detail.width / WIN;
  let win = { r: Math.floor((N - WIN) / 2), c: Math.floor((N - WIN) / 2) };

  function drawAll() {
    const pal = colors();
    paint(overview, REAL, 0, 0, N, OV, pal);
    const ctx = overview.getContext("2d");
    ctx.strokeStyle = pal.window;
    ctx.lineWidth = 2;
    ctx.strokeRect(win.c * OV + 1, win.r * OV + 1, WIN * OV - 2, WIN * OV - 2);
    paint(detail, REAL, win.r, win.c, WIN, DT, pal);
    paint(example, SAMPLE, 0, 0, SAMPLE.length, example.width / SAMPLE.length, pal);
    overviewReadout.innerHTML = `window at row <b>${win.r}</b>, col <b>${win.c}</b> · rows ${win.r}–${win.r + WIN - 1}, cols ${win.c}–${win.c + WIN - 1}`;
  }

  function clamp(v) { return Math.max(0, Math.min(N - WIN, v)); }

  function cellAt(canvas, event, cell) {
    const box = canvas.getBoundingClientRect();
    const scale = canvas.width / box.width;
    const x = (event.clientX - box.left) * scale;
    const y = (event.clientY - box.top) * scale;
    return { r: Math.floor(y / cell), c: Math.floor(x / cell) };
  }

  let dragging = false;
  function moveWindow(event) {
    const at = cellAt(overview, event, OV);
    win = { r: clamp(at.r - WIN / 2), c: clamp(at.c - WIN / 2) };
    drawAll();
  }
  overview.addEventListener("pointerdown", (e) => { dragging = true; overview.classList.add("dragging"); overview.setPointerCapture(e.pointerId); moveWindow(e); });
  overview.addEventListener("pointermove", (e) => { if (dragging) moveWindow(e); });
  overview.addEventListener("pointerup", () => { dragging = false; overview.classList.remove("dragging"); });
  overview.addEventListener("keydown", (e) => {
    const step = e.shiftKey ? WIN : 1;
    if (e.key === "ArrowUp") win.r = clamp(win.r - step);
    else if (e.key === "ArrowDown") win.r = clamp(win.r + step);
    else if (e.key === "ArrowLeft") win.c = clamp(win.c - step);
    else if (e.key === "ArrowRight") win.c = clamp(win.c + step);
    else return;
    e.preventDefault();
    drawAll();
  });
  overview.tabIndex = 0;

  detail.addEventListener("pointermove", (e) => {
    const at = cellAt(detail, e, DT);
    if (at.r < 0 || at.c < 0 || at.r >= WIN || at.c >= WIN) return;
    const r = win.r + at.r, c = win.c + at.c;
    const ch = REAL[r][c];
    const name = ch === "O" ? "sea monster" : ch === "#" ? "rough water" : "water";
    detailReadout.innerHTML = `row <b>${r}</b>, col <b>${c}</b> · <b>${ch}</b> ${name}`;
  });
  detail.addEventListener("pointerleave", () => { detailReadout.textContent = "hover a cell"; });

  drawAll();
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", drawAll);
  new MutationObserver(drawAll).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
</script>
"""


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

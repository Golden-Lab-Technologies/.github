"""Build profile/assets/banner.svg with every word converted to Poppins outlines.

GitHub serves README images as plain <img> SVG, which cannot load web fonts, so the
brand typeface only survives as paths. Run from the repository root:

    uv run --with fonttools --with uharfbuzz python tools/build_banner.py
"""

from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
OUT = ROOT / "profile" / "assets" / "banner.svg"

# Brand tokens: golden-lab-site/facts.json (updated 2026-10-02)
CREAM = "#F8F0E5"
LIGHT_GOLD = "#E7CE97"
BRASS = "#C9A24B"
WINE = "#57102B"
DEEP_WINE = "#3F0A1F"
ROSE_TINT = "#E7CFDA"

W, H = 1280, 440


class Face:
    def __init__(self, weight: str) -> None:
        path = FONTS / f"Poppins-{weight}.ttf"
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        self.hb_font = hb.Font(hb.Face(path.read_bytes()))

    def path(self, text: str, x: float, y: float, size: float, tracking: float = 0.0) -> tuple[str, float]:
        """Return SVG path data for `text` with its baseline at (x, y), and the advance width."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb_font, buf, {"kern": True, "liga": True})
        scale = size / self.upem
        pen = SVGPathPen(self.glyphs)
        cursor = 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = self.order[info.codepoint]
            gx = x + (cursor + pos.x_offset) * scale
            gy = y - pos.y_offset * scale
            self.glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, gx, gy)))
            cursor += pos.x_advance + tracking * self.upem
        return pen.getCommands(), cursor * scale


def text(face: Face, s: str, x: float, y: float, size: float, fill: str, tracking: float = 0.0) -> str:
    d, _ = face.path(s, x, y, size, tracking)
    return f'<path fill="{fill}" d="{d}"/>'


def mark(x: float, y: float, size: float, fill: str) -> str:
    # Exact mark geometry from facts.json brand_tokens; never redrawn.
    s = size / 200
    return (
        f'<g transform="translate({x} {y}) scale({s:.4f})" fill="{fill}">'
        '<path d="M78 0 L100 0 L100 100 L0 100 L0 78 A78 78 0 0 0 78 0 Z"/>'
        '<path d="M100 100 L200 100 L200 122 A78 78 0 0 0 122 200 L100 200 Z"/></g>'
    )


def trailer(regular: Face, mx: float) -> str:
    """Schematic of the trailer: geometry only, no dimensions claimed."""
    g = BRASS
    ground = 384
    parts = [
        f'<line x1="{mx - 230}" y1="{ground}" x2="{mx + 200}" y2="{ground}" stroke="{g}" stroke-opacity=".28" stroke-width="1.5"/>',
        # Body, wheel, tongue and hitch
        f'<rect x="{mx - 160}" y="322" width="196" height="42" rx="6" fill="{DEEP_WINE}" stroke="{g}" stroke-width="2"/>',
        f'<circle cx="{mx - 62}" cy="368" r="15" fill="{DEEP_WINE}" stroke="{g}" stroke-width="2"/>',
        f'<circle cx="{mx - 62}" cy="368" r="5" fill="{g}"/>',
        f'<path d="M{mx - 160} 352 L{mx - 214} 360" stroke="{g}" stroke-width="2" stroke-linecap="round"/>',
        f'<circle cx="{mx - 218}" cy="361" r="4" fill="none" stroke="{g}" stroke-width="2"/>',
        # Solar array on a tilted frame, with cell divisions
        f'<path d="M{mx - 120} 322 L{mx - 112} 302 M{mx - 40} 322 L{mx - 48} 286" stroke="{g}" stroke-width="2"/>',
        f'<polygon points="{mx - 152},304 {mx - 30},270 {mx - 22},288 {mx - 144},322" fill="{WINE}" stroke="{g}" stroke-width="2" stroke-linejoin="round"/>',
    ]
    for t in (0.25, 0.5, 0.75):
        x1, y1 = mx - 152 + 122 * t, 304 - 34 * t
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1 + 8:.1f}" y2="{y1 + 18:.1f}" stroke="{g}" stroke-opacity=".6" stroke-width="1.2"/>')
    parts.append(f'<line x1="{mx - 148}" y1="313" x2="{mx - 26}" y2="279" stroke="{g}" stroke-opacity=".6" stroke-width="1.2"/>')
    # Telescoping mast: three nested sections
    parts += [
        f'<rect x="{mx - 8}" y="236" width="16" height="86" rx="2" fill="{DEEP_WINE}" stroke="{g}" stroke-width="2"/>',
        f'<rect x="{mx - 5.5}" y="156" width="11" height="80" rx="2" fill="{DEEP_WINE}" stroke="{g}" stroke-width="2"/>',
        f'<rect x="{mx - 3}" y="98" width="6" height="58" rx="1.5" fill="{DEEP_WINE}" stroke="{g}" stroke-width="2"/>',
        # Crossbar with two floodlights
        f'<line x1="{mx - 28}" y1="98" x2="{mx + 28}" y2="98" stroke="{g}" stroke-width="2.5" stroke-linecap="round"/>',
        f'<rect x="{mx - 34}" y="99" width="14" height="9" rx="2" fill="{LIGHT_GOLD}"/>',
        f'<rect x="{mx + 20}" y="99" width="14" height="9" rx="2" fill="{LIGHT_GOLD}"/>',
        # Gateway enclosure and radiating signal
        f'<rect x="{mx - 11}" y="74" width="22" height="18" rx="3" fill="{DEEP_WINE}" stroke="{g}" stroke-width="2"/>',
        f'<line x1="{mx}" y1="92" x2="{mx}" y2="98" stroke="{g}" stroke-width="2"/>',
    ]
    for r, op in ((12, 1), (21, 0.7), (30, 0.4)):
        parts.append(
            f'<path d="M{mx - r * 0.87:.1f} {66 - r * 0.5:.1f} A{r} {r} 0 0 1 {mx + r * 0.87:.1f} {66 - r * 0.5:.1f}" '
            f'fill="none" stroke="{LIGHT_GOLD}" stroke-opacity="{op}" stroke-width="2" stroke-linecap="round"/>'
        )
    # Camera on the middle section
    parts.append(f'<rect x="{mx + 6}" y="172" width="18" height="11" rx="3" fill="{DEEP_WINE}" stroke="{g}" stroke-width="2"/>')
    parts.append(f'<circle cx="{mx + 24}" cy="177.5" r="2.5" fill="{LIGHT_GOLD}"/>')

    # Callouts: leader, node, label
    lx = mx + 70
    for y, x0, label in (
        (44, mx + 28, "Wi-Fi / 5G"),
        (83, mx + 12, "IoT / RTLS gateway"),
        (110, mx + 35, "LED floodlights"),
        (178, mx + 27, "Cameras"),
    ):
        parts.append(f'<path d="M{x0} {y} H{lx - 8}" stroke="{g}" stroke-opacity=".55" stroke-width="1.2"/>')
        parts.append(f'<circle cx="{x0}" cy="{y}" r="2.5" fill="{g}"/>')
        parts.append(text(regular, label, lx, y + 5, 15, CREAM))
    parts.append(f'<path d="M{mx - 90} 287 V250" stroke="{g}" stroke-opacity=".55" stroke-width="1.2"/>')
    parts.append(f'<circle cx="{mx - 90}" cy="287" r="2.5" fill="{g}"/>')
    parts.append(text(regular, "Solar + battery", mx - 152, 241, 15, CREAM))
    return "\n  ".join(parts)


def main() -> None:
    light, regular, medium, semibold = (Face(w) for w in ("Light", "Regular", "Medium", "SemiBold"))
    left = 76
    body = [
        mark(left, 62, 44, CREAM),
        text(regular, "Golden Lab Technologies", left + 62, 92, 21, CREAM, tracking=0.01),
        text(semibold, "Power & connectivity,", left, 200, 58, CREAM, tracking=-0.02),
        text(semibold, "anywhere you park it.", left, 268, 58, LIGHT_GOLD, tracking=-0.02),
        text(light, "Solar-powered infrastructure trailers and", left, 320, 22, ROSE_TINT),
        text(light, "carrier-grade network engineering.", left, 352, 22, ROSE_TINT),
        text(medium, "VETERAN-OWNED  ·  LEXINGTON, KENTUCKY  ·  SINCE 2024", left, 394, 13, BRASS, tracking=0.12),
        trailer(regular, 1010),
    ]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Golden Lab Technologies</title>
  <desc id="d">Power and connectivity, anywhere you park it. Solar-powered infrastructure trailers with a telescoping mast carrying Wi-Fi and 5G, an IoT and RTLS gateway, LED floodlights and cameras.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{WINE}"/><stop offset="1" stop-color="#2E0716"/></linearGradient>
    <radialGradient id="sun" cx="1010" cy="70" r="330" gradientUnits="userSpaceOnUse"><stop stop-color="{BRASS}" stop-opacity=".2"/><stop offset="1" stop-color="{BRASS}" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="{W}" height="{H}" rx="20" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" rx="20" fill="url(#sun)"/>
  {chr(10).join("  " + b for b in body)}
</svg>
"""
    OUT.write_text(svg)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()

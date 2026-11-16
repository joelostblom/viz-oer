"""Direct SVG channel diagrams: Python standard library only, no Altair.

Run this file to write *-channels-direct.svg comparison images into assets/images/.
The two public functions return SVG strings and do not write files on import.

Adapted from Visualization Analysis and Design, Tamara Munzner, illustrations
by Eamonn Maguire, CRC Press, 2014 (CC BY 4.0 diagrams):
https://www.cs.ubc.ca/~tmm/vadbook/figures.html
"""

from html import escape
from math import atan2, degrees, floor, hypot, isfinite, sqrt
from pathlib import Path


def _number(value):
    return f"{value:.4f}".rstrip("0").rstrip(".") if isinstance(value, float) else str(value)


def _tag(name, content=None, **attributes):
    attrs = " ".join(
        f'{key.replace("_", "-")}="{escape(_number(value), quote=True)}"'
        for key, value in attributes.items()
    )
    opening = f"<{name}{' ' + attrs if attrs else ''}"
    return f"{opening}/>" if content is None else f"{opening}>{content}</{name}>"


class _Diagram:
    def __init__(self, rows, columns, scale, title):
        if not isfinite(scale) or scale <= 0:
            raise ValueError("scale must be a finite positive number")
        self.width, self.height = columns * 564 + (columns - 1) * 24, rows * 120
        self.scale = scale
        self.parts = [
            _tag("title", escape(title), id="title"),
            _tag("desc", "Classical, context-dependent channel guidance. Adapted from "
                 "Munzner and Maguire, Visualization Analysis and Design (2014), CC BY 4.0.",
                 id="description"),
        ]
        self.add("rect", width=self.width, height=self.height, fill="white")
        for column in range(columns):
            x = column * 588
            for row in range(rows):
                if (row + column * rows) % 2:
                    self.add("rect", x=x, y=row * 120, width=564, height=120, fill="#ebebeb")
            self.add("rect", x=x, width=48, height=self.height, fill="#262626")
            for row in range(rows):
                self.text(x + 22, row * 120 + 60, str(column * rows + row + 1),
                          size=26, fill="white", text_anchor="middle")

    def add(self, tag, content=None, **attributes):
        self.parts.append(_tag(tag, content, **attributes))

    def text(self, x, y, value, size=18, **attributes):
        # Match the reference's rounded screen-pixel text baseline adjustment.
        baseline = floor(size * self.scale * 0.3 + 0.5) / self.scale
        content = "".join(_tag("tspan", escape(line), x=x, dy=0 if i == 0 else 24)
                          for i, line in enumerate(value.split("\n")))
        self.add("text", content, x=x, y=y + baseline, font_size=size, **attributes)

    def line(self, x, y, x2, y2, **attributes):
        self.add("path", d=f"M{_number(x)} {_number(y)}L{_number(x2)} {_number(y2)}",
                 fill="none", stroke="#444", **attributes)

    def finish(self):
        return _tag("svg", "\n".join(self.parts), xmlns="http://www.w3.org/2000/svg",
                    width=self.width * self.scale, height=self.height * self.scale,
                    viewBox=f"0 0 {self.width} {self.height}", font_family="sans-serif",
                    fill="#444", role="img", aria_labelledby="title description") + "\n"


def grouping_channels_svg(scale: float = 0.8) -> str:
    """Draw proximity, hue, and shape examples with reusable SVG symbols."""
    svg = _Diagram(3, 1, scale, "Classical static identity channels for grouping")
    radius = sqrt(160) / 2
    half_height = radius * sqrt(3) / 2
    svg.add("defs", "".join([
        _tag("circle", id="dot", r=radius),
        _tag("rect", id="square", x=-radius, y=-radius, width=2 * radius, height=2 * radius),
        _tag("path", id="triangle", d=f"M0 {-half_height:.4f}L{-radius:.4f} "
             f"{half_height:.4f}H{radius:.4f}Z"),
    ]))
    for y, label in [(48, "Spatial region\n(position)"), (180, "Color hue"), (300, "Shape")]:
        svg.text(397, y, label, font_weight="bold", fill="#222")
    for center in (123, 220, 317):
        for dx, dy in [(-14, -14), (14, -14), (-14, 14), (14, 14)]:
            svg.add("use", href="#dot", x=center + dx, y=60 + dy)
    for row in range(3):
        for col in range(4):
            group, x, y = (row + col) % 3, 105 + col * 70, 156 + row * 24
            svg.add("use", href="#dot", x=x, y=y, fill=("#0072b2", "#d55e00", "#009e73")[group])
            svg.add("use", href=("#dot", "#square", "#triangle")[group], x=x, y=y + 120)
    return svg.finish()


def magnitude_channels_svg(scale: float = 0.55) -> str:
    """Draw all ten magnitude examples directly, using exact quadratic curves."""
    svg = _Diagram(5, 2, scale, "Classical visual channels for quantitative magnitude judgments")
    for x, y, label in [
        (397, 48, "Position on\na common scale"), (397, 156, "Position on\nunaligned\nscales"),
        (397, 300, "Length"), (397, 420, "Tilt or Angle"), (397, 540, "Area (2D as size)"),
        (985, 48, "Depth\n(3D as position)"), (985, 168, "Color luminance\nor brightness"),
        (985, 288, "Color saturation\nor intensity"), (985, 420, "Curvature"),
        (985, 528, "Volume\n(3D as size)"),
    ]:
        svg.text(x, y, label, font_weight="bold", fill="#222")
    for left, y in [(118, 67), (92, 150), (155, 206)]:
        svg.line(left, y, left + 190, y, stroke_width=5)
        for value in (0, 5, 10):
            x = left + value * 19
            svg.line(x, y - 8, x, y + 8, stroke_width=5)
            svg.text(x, y + 20, str(value), size=14, text_anchor="middle")
    for x, y in [(160, 27), (274, 27), (231, 150), (294, 206)]:
        svg.add("circle", cx=x, cy=y, r=15, stroke="#222", stroke_width=2)
    for x, y, x2, y2 in [
        (125, 280, 330, 280), (87, 315, 240, 315),
        (118, 462, 118, 379), (138, 462, 184, 379), (168, 462, 239, 392),
        (213, 466, 284, 417), (264, 468, 354, 451),
    ]:
        svg.line(x, y, x2, y2, stroke_width=5, stroke_linecap="round")
    for x, side in [(100, 25), (152, 38), (216, 51), (292, 64)]:
        svg.add("rect", x=x, y=583 - side, width=side, height=side, stroke="#222", stroke_width=2)

    # Depth arrows: short perpendicular baseline, shaft, triangular head, dot.
    for x, y, x2, y2, size in [(743, 105, 718, 50, 480), (813, 105, 873, 20, 750)]:
        dx, dy = x2 - x, y2 - y
        ux, uy = dx / hypot(dx, dy), dy / hypot(dx, dy)
        hx, hy = x2 - ux * 18, y2 - uy * 18
        svg.line(x, y, hx, hy, stroke_width=4)
        svg.line(x - uy * 6, y + ux * 6, x + uy * 6, y - ux * 6, stroke_width=4)
        radius, half_height = sqrt(240) / 2, sqrt(180) / 2
        svg.add("path", d=f"M0 {-half_height:.4f}L{-radius:.4f} {half_height:.4f}"
                f"H{radius:.4f}Z", transform=f"translate({hx:.4f} {hy:.4f}) "
                f"rotate({degrees(atan2(dx, -dy)):.4f})")
        svg.add("circle", cx=x2, cy=y2, r=sqrt(size) / 2, stroke="#222", stroke_width=2)
    for y, colors in [(157, ["white", "#d0d0d0", "#929292", "#444"]),
                      (277, ["#ffe0e0", "#faa", "#f55", "#ff2600"])]:
        for i, color in enumerate(colors):
            svg.add("rect", x=676 + 70 * i, y=y, width=46, height=46,
                    fill=color, stroke="#555", stroke_width=1.5)
    # A single quadratic Bézier represents each formerly 41-point curve.
    for x, bend in [(698, 0), (752, 13), (812, 26), (872, 56)]:
        svg.add("path", d=f"M{x} 382Q{x + 2 * bend} 420 {x} 458", fill="none",
                stroke="#444", stroke_width=4, stroke_linecap="round")
    for center, half_width, height in [(698, 23, 15), (768, 25, 28), (843, 26, 43), (923, 26, 58)]:
        depth = half_width / 2
        y = 579 - height - depth
        top, left = (center, y - depth), (center - half_width, y)
        front, right = (center, y + depth), (center + half_width, y)
        bottom = (center, 579)
        for color, points in [
            ("#fafafa", [left, front, bottom, (left[0], y + height)]),
            ("#d4d4d4", [front, right, (right[0], y + height), bottom]),
            ("#eee", [top, right, front, left]),
        ]:
            svg.add("polygon", points=" ".join(f"{_number(x)},{_number(y)}" for x, y in points),
                    fill=color, stroke="#888", stroke_width=1.5, stroke_linejoin="round")
    return svg.finish()


if __name__ == "__main__":
    for name, drawing in [("grouping", grouping_channels_svg()), ("magnitude", magnitude_channels_svg())]:
        path = Path(__file__).resolve().parents[3] / "assets/images" / f"{name}-channels-direct.svg"
        path.write_text(drawing, encoding="utf-8")
        print(f"Saved {path}")

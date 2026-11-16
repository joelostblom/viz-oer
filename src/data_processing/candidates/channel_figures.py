"""Reusable Altair diagrams for categorical identity and quantitative magnitude.

Call ``grouping_channels()`` or ``magnitude_channels()`` in a Python cell.
Both return an editable LayerChart and accept ``scale`` (default 0.8).
The module has no file-writing or renderer-changing side effects on import.
Run ``uv run python src/data_processing/candidates/channel_figures.py`` from the repository root
to regenerate the SVG illustrations embedded in the textbook.

Adapted from Visualization Analysis and Design, Tamara Munzner, with
illustrations by Eamonn Maguire, CRC Press, 2014 (figures CC BY 4.0).
https://www.cs.ubc.ca/~tmm/vadbook/figures.html
Magnitude layout reference:
https://viz-learn.mds.ubc.ca/module2/visual-channels-rank.png
Grouping examples are newly drawn following the static identity-channel order.
"""

from math import atan2, degrees, hypot, isfinite
from pathlib import Path

import altair as alt


def _marks(records, width, height):
    """Use shared diagram coordinates, with y increasing down the page."""
    return alt.Chart(alt.Data(values=records)).encode(
        x=alt.X("x:Q", scale=alt.Scale(domain=[0, width]), axis=None),
        y=alt.Y("y:Q", scale=alt.Scale(domain=[height, 0]), axis=None),
    )


def _resize_diagram(chart, scale):
    if not isfinite(scale) or scale <= 0:
        raise ValueError("scale must be a finite positive number")
    resized = chart.copy(deep=True)
    resized.width = chart.width * scale
    resized.height = chart.height * scale
    # Coordinates scale through their output ranges. Pixel-based properties
    # need separate scaling; symbol sizes are areas, not lengths.
    for layer in resized.layer:
        mark = {"type": layer.mark} if isinstance(layer.mark, str) else layer.mark.to_dict()
        for key in ("fontSize", "lineHeight", "strokeWidth"):
            if key in mark:
                mark[key] *= scale
        if "size" in mark:
            mark["size"] *= scale**2
        layer.mark = alt.MarkDef.from_dict(mark)
        for row in layer.data.values:
            if "size" in row:
                row["size"] *= scale**2
    return resized


def grouping_channels(scale: float = 0.8) -> alt.LayerChart:
    """Illustrate spatial region, hue, and shape for categorical grouping."""
    width, height = 564, 360
    ink = "#444444"

    def marks(records):
        return _marks(records, width, height)

    backgrounds = marks([
        {"x": 0, "x2": width, "y": i * 120, "y2": (i + 1) * 120,
         "fill": "#ffffff" if i % 2 == 0 else "#ebebeb"}
        for i in range(3)
    ]).mark_rect().encode(
        x2="x2:Q", y2="y2:Q",
        color=alt.Color("fill:N", scale=None, legend=None),
    )
    sidebar = marks([
        {"x": 0, "x2": 48, "y": 0, "y2": height},
    ]).mark_rect(color="#262626").encode(x2="x2:Q", y2="y2:Q")
    ranks = marks([
        {"x": 22, "y": i * 120 + 60, "text": str(i + 1)}
        for i in range(3)
    ]).mark_text(fontSize=26, color="white").encode(text="text:N")
    labels = marks([
        {"x": 397, "y": 48, "text": "Spatial region\n(position)"},
        {"x": 397, "y": 180, "text": "Color hue"},
        {"x": 397, "y": 300, "text": "Shape"},
    ]).mark_text(
        align="left", baseline="middle", lineBreak="\n", lineHeight=24,
        fontSize=18, fontWeight="bold", color="#222222",
    ).encode(text="text:N")
    regions = marks([
        {"x": center + dx, "y": 60 + dy}
        for center in (123, 220, 317)
        for dx, dy in [(-14, -14), (14, -14), (-14, 14), (14, 14)]
    ]).mark_point(shape="circle", filled=True, size=160, color=ink, opacity=1)

    # Identical category arrangements isolate hue versus shape, with groups
    # interleaved so that proximity alone does not separate them.
    categories = [
        {"x": 105 + col * 70, "y": 156 + row * 24, "group": (col + row) % 3}
        for row in range(3) for col in range(4)
    ]
    colors = ("#0072b2", "#d55e00", "#009e73")
    hues = marks([
        {**point, "fill": colors[point["group"]]} for point in categories
    ]).mark_point(shape="circle", filled=True, size=160, opacity=1).encode(
        color=alt.Color("fill:N", scale=None, legend=None),
    )
    shapes = marks([
        {**point, "y": point["y"] + 120} for point in categories
    ]).mark_point(filled=True, size=160, color=ink, opacity=1).encode(
        shape=alt.Shape(
            "group:N",
            scale=alt.Scale(domain=[0, 1, 2], range=["circle", "square", "triangle-up"]),
            legend=None,
        ),
    )
    diagram = alt.layer(
        backgrounds, sidebar, ranks, labels, regions, hues, shapes,
    ).properties(
        width=width, height=height, background="white", padding=0,
        usermeta={
            "description": "Classical identity-channel ordering; motion omitted."
            " Context-dependent guidance, not a universal grouping-performance ranking.",
            "reference": "https://www.cs.ubc.ca/~tmm/vadbook/figures.html",
        },
    ).configure_view(strokeOpacity=0)
    return _resize_diagram(diagram, scale)


def export_channel_figures() -> None:
    """Export the textbook's static illustrations at their current display sizes."""
    output_dir = Path(__file__).resolve().parents[3] / "assets/images"
    for name, chart in [
        ("grouping-channels", grouping_channels()),
        ("magnitude-channels", magnitude_channels(scale=0.55)),
    ]:
        path = output_dir / f"{name}.svg"
        chart.save(path)
        print(f"Saved {path}")


def magnitude_channels(scale: float = 0.8) -> alt.LayerChart:
    """Illustrate the ten classical magnitude channels in two columns."""
    column_width, height = 564, 600
    right = column_width + 24
    width = right + column_width
    ink = "#444444"

    def marks(records):
        return _marks(records, width, height)

    backgrounds = marks([
        {"x": offset, "x2": offset + column_width,
         "y": i * 120, "y2": (i + 1) * 120,
         "fill": "#ffffff" if (i + column * 5) % 2 == 0 else "#ebebeb"}
        for column, offset in enumerate((0, right)) for i in range(5)
    ]).mark_rect().encode(
        x2="x2:Q", y2="y2:Q", color=alt.Color("fill:N", scale=None, legend=None),
    )
    sidebar = marks([
        {"x": offset, "x2": offset + 48, "y": 0, "y2": height}
        for offset in (0, right)
    ]).mark_rect(color="#262626").encode(x2="x2:Q", y2="y2:Q")
    ranks = marks([
        {"x": offset + 22, "y": i * 120 + 60, "text": str(i + column * 5 + 1)}
        for column, offset in enumerate((0, right)) for i in range(5)
    ]).mark_text(fontSize=26, color="white").encode(text="text:N")
    labels = marks([
        {"x": 397, "y": 48, "text": "Position on\na common scale"},
        {"x": 397, "y": 156, "text": "Position on\nunaligned\nscales"},
        {"x": 397, "y": 300, "text": "Length"},
        {"x": 397, "y": 420, "text": "Tilt or Angle"},
        {"x": 397, "y": 540, "text": "Area (2D as size)"},
        {"x": right + 397, "y": 48, "text": "Depth\n(3D as position)"},
        {"x": right + 397, "y": 168, "text": "Color luminance\nor brightness"},
        {"x": right + 397, "y": 288, "text": "Color saturation\nor intensity"},
        {"x": right + 397, "y": 420, "text": "Curvature"},
        {"x": right + 397, "y": 528, "text": "Volume\n(3D as size)"},
    ]).mark_text(
        align="left", baseline="middle", lineBreak="\n", lineHeight=24,
        fontSize=18, fontWeight="bold", color="#222222",
    ).encode(text="text:N")

    scales = [(118, 308, 67), (92, 282, 150), (155, 345, 206)]
    rules, ticks, tick_labels = [], [], []
    for left, scale_end, y in scales:
        rules.append({"x": left, "x2": scale_end, "y": y, "y2": y})
        for value in (0, 5, 10):
            x = left + (scale_end - left) * value / 10
            ticks.append({"x": x, "y": y - 8, "y2": y + 8})
            tick_labels.append({"x": x, "y": y + 20, "text": str(value)})
    axes = marks(rules).mark_rule(color=ink, strokeWidth=5).encode(x2="x2:Q", y2="y2:Q")
    tick_marks = marks(ticks).mark_rule(color=ink, strokeWidth=5).encode(y2="y2:Q")
    numbers = marks(tick_labels).mark_text(color=ink, fontSize=14).encode(text="text:N")
    positions = marks([
        {"x": 160, "y": 27}, {"x": 274, "y": 27},
        {"x": 231, "y": 150}, {"x": 294, "y": 206},
    ]).mark_point(
        shape="circle", filled=True, size=900, color=ink,
        stroke="#222222", strokeWidth=2, opacity=1,
    )
    lengths = marks([
        {"x": 125, "x2": 330, "y": 280, "y2": 280},
        {"x": 87, "x2": 240, "y": 315, "y2": 315},
    ]).mark_rule(color=ink, strokeWidth=5, strokeCap="round").encode(x2="x2:Q", y2="y2:Q")
    angles = marks([
        {"x": 118, "y": 462, "x2": 118, "y2": 379},
        {"x": 138, "y": 462, "x2": 184, "y2": 379},
        {"x": 168, "y": 462, "x2": 239, "y2": 392},
        {"x": 213, "y": 466, "x2": 284, "y2": 417},
        {"x": 264, "y": 468, "x2": 354, "y2": 451},
    ]).mark_rule(color=ink, strokeWidth=5, strokeCap="round").encode(x2="x2:Q", y2="y2:Q")
    areas = marks([
        {"x": x, "x2": x + side, "y": 583 - side, "y2": 583}
        for x, side in [(100, 25), (152, 38), (216, 51), (292, 64)]
    ]).mark_rect(color=ink, stroke="#222222", strokeWidth=2).encode(x2="x2:Q", y2="y2:Q")

    depth_rules, depth_heads, depth_dots = [], [], []
    for x, y, x2, y2, size in [(155, 105, 130, 50, 480), (225, 105, 285, 20, 750)]:
        dx, dy = x2 - x, y2 - y
        distance = hypot(dx, dy)
        ux, uy = dx / distance, dy / distance
        head_x, head_y = x2 - ux * 18, y2 - uy * 18
        depth_rules.extend([
            {"x": right + x, "y": y, "x2": right + head_x, "y2": head_y},
            {"x": right + x - uy * 6, "y": y + ux * 6,
             "x2": right + x + uy * 6, "y2": y - ux * 6},
        ])
        depth_heads.append({
            "x": right + head_x, "y": head_y, "angle": degrees(atan2(dx, -dy)),
        })
        depth_dots.append({"x": right + x2, "y": y2, "size": size})
    depth = marks(depth_rules).mark_rule(color=ink, strokeWidth=4).encode(x2="x2:Q", y2="y2:Q")
    arrowheads = marks(depth_heads).mark_point(
        shape="triangle-up", size=240, filled=True, color=ink, opacity=1,
    ).encode(angle=alt.Angle("angle:Q", scale=None))
    depth_points = marks(depth_dots).mark_point(
        filled=True, color=ink, stroke="#222222", strokeWidth=2, opacity=1,
    ).encode(size=alt.Size("size:Q", scale=None, legend=None))

    swatches = marks([
        {"x": right + 88 + i * 70, "x2": right + 134 + i * 70,
         "y": y, "y2": y + 46, "fill": color}
        for y, colors in [
            (157, ["#ffffff", "#d0d0d0", "#929292", ink]),
            (277, ["#ffe0e0", "#ffaaaa", "#ff5555", "#ff2600"]),
        ] for i, color in enumerate(colors)
    ]).mark_rect(stroke="#555555", strokeWidth=1.5).encode(
        x2="x2:Q", y2="y2:Q", color=alt.Color("fill:N", scale=None, legend=None),
    )
    curves = marks([
        {"x": right + x + bend * 4 * (step / 40) * (1 - step / 40),
         "y": 382 + 76 * step / 40, "curve": i, "order": step}
        for i, (x, bend) in enumerate([(110, 0), (164, 13), (224, 26), (284, 56)])
        for step in range(41)
    ]).mark_line(color=ink, strokeWidth=4, strokeCap="round").encode(
        detail="curve:N", order="order:Q",
    )

    # Three closed, filled line paths form each isometric box.
    faces = []
    for cube, (center, half_width, box_height) in enumerate([
        (110, 23, 15), (180, 25, 28), (255, 26, 43), (335, 26, 58),
    ]):
        center += right
        half_depth = half_width / 2
        y = 579 - box_height - half_depth
        top, left = (center, y - half_depth), (center - half_width, y)
        front, back = (center, y + half_depth), (center + half_width, y)
        bottom = (center, y + half_depth + box_height)
        for face, color, vertices in [
            ("left", "#fafafa", [left, front, bottom, (left[0], y + box_height)]),
            ("right", "#d4d4d4", [front, back, (back[0], y + box_height), bottom]),
            ("top", "#eeeeee", [top, back, front, left]),
        ]:
            for order, (x, y_vertex) in enumerate([*vertices, vertices[0]]):
                faces.append({
                    "x": x, "y": y_vertex, "face": f"{cube}-{face}",
                    "order": order, "fill": color,
                })
    volumes = marks(faces).mark_line(
        filled=True, stroke="#888888", strokeWidth=1.5, strokeJoin="round",
    ).encode(
        detail="face:N", order="order:Q", fill=alt.Fill("fill:N", scale=None, legend=None),
    )
    diagram = alt.layer(
        backgrounds, sidebar, ranks, labels, axes, tick_marks, numbers,
        positions, lengths, angles, areas, depth, arrowheads, depth_points,
        swatches, curves, volumes,
    ).properties(
        width=width, height=height, background="white", padding=0,
    ).configure_view(strokeOpacity=0)
    return _resize_diagram(diagram, scale)


if __name__ == "__main__":
    export_channel_figures()

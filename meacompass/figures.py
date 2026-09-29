"""Result-only tables and deterministic Pillow figures; never trains models."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


COLORS = ["#155EEF", "#12B76A", "#F79009", "#D92D20", "#7A5AF8", "#667085"]
BACKGROUND = "#FFFFFF"
INK = "#101828"
GRID = "#D0D5DD"


def require_columns(frame: pd.DataFrame, columns: set[str], source: Path) -> None:
    missing = columns - set(frame.columns)
    if missing:
        raise ValueError(f"{source} is missing required columns: {sorted(missing)}")


def load_required(path: Path, columns: set[str]) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Required saved result file is missing: {path}")
    frame = pd.read_csv(path)
    require_columns(frame, columns, path)
    return frame


def write_main_table(source: Path, output: Path, models: list[str] | None = None) -> None:
    columns = {
        "model", "endpoint", "mae_y12_mean", "spearman_y12_mean", "spearman_delta_mean"
    }
    frame = load_required(source, columns)
    if models:
        frame = frame.loc[frame["model"].isin(models)]
    if frame.empty:
        raise ValueError("Main-results model filter produced no rows")
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.sort_values(["endpoint", "model"]).to_csv(output, index=False)


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _canvas(title: str, width: int = 1400, height: int = 850) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.text((70, 35), title, fill=INK, font=_font(34, bold=True))
    return image, draw


def _bounds(values: list[float]) -> tuple[float, float]:
    low, high = min(values), max(values)
    if low == high:
        return low - 0.5, high + 0.5
    padding = 0.08 * (high - low)
    return low - padding, high + padding


def _line_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    series: list[tuple[str, list[float], list[float]]],
    x_label: str,
    y_label: str,
) -> None:
    left, top, right, bottom = box
    all_x = [value for _, xs, _ in series for value in xs]
    all_y = [value for _, _, ys in series for value in ys]
    x_low, x_high = _bounds(all_x)
    y_low, y_high = _bounds(all_y)
    draw.line((left, bottom, right, bottom), fill=INK, width=2)
    draw.line((left, top, left, bottom), fill=INK, width=2)
    for tick in range(6):
        y = top + tick * (bottom - top) / 5
        draw.line((left, y, right, y), fill=GRID, width=1)
        value = y_high - tick * (y_high - y_low) / 5
        draw.text((left - 70, y - 9), f"{value:.1f}", fill=INK, font=_font(16))
    for tick in range(5):
        x = left + tick * (right - left) / 4
        value = x_low + tick * (x_high - x_low) / 4
        label = f"{value:.0f}" if x_high - x_low > 2 else f"{value:.2f}"
        draw.line((x, bottom, x, bottom + 7), fill=INK, width=2)
        draw.text((x - 18, bottom + 12), label, fill=INK, font=_font(15))
    for index, (label, xs, ys) in enumerate(series):
        color = COLORS[index % len(COLORS)]
        points = [
            (
                left + (x - x_low) / (x_high - x_low) * (right - left),
                bottom - (y - y_low) / (y_high - y_low) * (bottom - top),
            )
            for x, y in zip(xs, ys, strict=True)
        ]
        if len(points) > 1:
            draw.line(points, fill=color, width=4)
        for point in points:
            draw.ellipse((point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5), fill=color)
        legend_y = top + index * 28
        draw.rectangle((right + 25, legend_y, right + 45, legend_y + 12), fill=color)
        draw.text((right + 52, legend_y - 5), label, fill=INK, font=_font(16))
    draw.text(((left + right) / 2 - 50, bottom + 42), x_label, fill=INK, font=_font(18))
    draw.text((left, top - 32), y_label, fill=INK, font=_font(18))


def _save(image: Image.Image, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def plot_risk_coverage(source: Path, output: Path) -> None:
    frame = load_required(source, {"endpoint", "model", "coverage", "mae"})
    series = []
    for (endpoint, model), part in frame.groupby(["endpoint", "model"], sort=True):
        part = part.sort_values("coverage")
        series.append((f"{endpoint} · {model}", part["coverage"].tolist(), part["mae"].tolist()))
    image, draw = _canvas("Risk–coverage: lower accepted-case MAE is better")
    _line_panel(draw, (120, 130, 1040, 720), series, "Accepted coverage", "Accepted-case MAE")
    _save(image, output)


def plot_time_ablation(source: Path, output: Path) -> None:
    frame = load_required(
        source, {"endpoint", "input_window", "decision_day", "mae", "coverage", "abstention_rate"}
    )
    accuracy = []
    abstention = []
    for endpoint, part in frame.groupby("endpoint", sort=True):
        part = part.sort_values("decision_day")
        accuracy.append((endpoint, part["decision_day"].tolist(), part["mae"].tolist()))
        abstention.append((endpoint, part["decision_day"].tolist(), (100 * part["abstention_rate"]).tolist()))
    image, draw = _canvas("Accuracy and abstention by decision day", width=1800)
    _line_panel(draw, (110, 150, 690, 710), accuracy, "Decision day", "MAE")
    _line_panel(draw, (970, 150, 1550, 710), abstention, "Decision day", "Abstention (%)")
    _save(image, output)


def plot_dose_strata(source: Path, output: Path) -> None:
    frame = load_required(source, {"endpoint", "model", "dose_stratum"})
    gain_column = (
        "relative_gain_percent"
        if "relative_gain_percent" in frame.columns
        else "relative_gain_vs_bt_plus_percent"
    )
    require_columns(frame, {gain_column}, source)
    pivot = frame.pivot_table(
        index="endpoint", columns="dose_stratum", values=gain_column, aggfunc="mean"
    ).fillna(0)
    image, draw = _canvas("Dose-stratified relative MAE gain vs BT+")
    left, top, right, bottom = 140, 140, 1240, 710
    values = pivot.to_numpy().flatten().tolist() + [0]
    low, high = _bounds(values)
    zero_y = bottom - (0 - low) / (high - low) * (bottom - top)
    draw.line((left, zero_y, right, zero_y), fill=INK, width=2)
    endpoints = pivot.index.tolist()
    strata = pivot.columns.tolist()
    group_width = (right - left) / len(endpoints)
    bar_width = group_width / (len(strata) + 1)
    for endpoint_index, endpoint in enumerate(endpoints):
        center = left + (endpoint_index + 0.5) * group_width
        for stratum_index, stratum in enumerate(strata):
            value = float(pivot.loc[endpoint, stratum])
            x0 = center + (stratum_index - len(strata) / 2) * bar_width
            y = bottom - (value - low) / (high - low) * (bottom - top)
            draw.rectangle((x0, min(y, zero_y), x0 + bar_width * 0.8, max(y, zero_y)), fill=COLORS[stratum_index % len(COLORS)])
        draw.text((center - 55, bottom + 25), endpoint, fill=INK, font=_font(14))
    for index, stratum in enumerate(strata):
        draw.rectangle((1020, 80 + index * 25, 1040, 92 + index * 25), fill=COLORS[index % len(COLORS)])
        draw.text((1048, 75 + index * 25), str(stratum), fill=INK, font=_font(15))
    _save(image, output)


def plot_calibration(source: Path, output: Path) -> None:
    frame = load_required(source, {"endpoint", "cohort", "nominal_coverage", "observed_coverage"})
    series = [("Ideal", [0.0, 1.0], [0.0, 1.0])]
    for (endpoint, cohort), part in frame.groupby(["endpoint", "cohort"], sort=True):
        series.append((f"{endpoint} · {cohort}", part["nominal_coverage"].tolist(), part["observed_coverage"].tolist()))
    image, draw = _canvas("Interval calibration", width=1650)
    _line_panel(draw, (120, 130, 1050, 720), series, "Nominal coverage", "Observed coverage")
    _save(image, output)

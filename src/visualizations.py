"""Publication-style Plotly components used by the editorial Streamlit pages."""

from __future__ import annotations

import textwrap

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PAPER = "#FAF8F2"
PAPER_SECONDARY = "#EAE4D8"
INK = "#1A1917"
SOFT_GREY = "#77736C"
BORDER = "#D4CEC2"
SUCCESS = "#496454"
WARNING = "#8A693D"
DANGER = "#813F39"
EDITORIAL_PALETTE = ["#40352C", "#6D5947", "#A89984", "#8A693D"]


def _editorial_layout(figure: go.Figure, *, height: int, margin: dict[str, int]) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font={"family": "Inter, Arial, sans-serif", "color": INK, "size": 12},
        # Plotly renders a literal ``undefined`` title when a title style exists
        # without title text in the current Streamlit integration. Keep the
        # intentional title-free charts explicit.
        title={
            "text": "",
            "font": {"family": "Georgia, Times New Roman, serif", "color": INK, "size": 18},
        },
        legend={
            "bgcolor": "rgba(250,248,242,.92)",
            "bordercolor": BORDER,
            "borderwidth": 1,
            "font": {"size": 11},
        },
        hoverlabel={
            "bgcolor": "#090909",
            "bordercolor": "#090909",
            "font": {"color": "#FAF8F2", "family": "Inter, Arial, sans-serif"},
        },
    )
    figure.update_xaxes(
        gridcolor=BORDER,
        zerolinecolor="#A89984",
        linecolor=BORDER,
        tickfont={"color": SOFT_GREY},
        title_font={"color": INK},
        automargin=True,
    )
    figure.update_yaxes(
        gridcolor=BORDER,
        zerolinecolor="#A89984",
        linecolor=BORDER,
        tickfont={"color": SOFT_GREY},
        title_font={"color": INK},
        automargin=True,
    )
    return figure


def confidence_gauge(
    misleading_probability: float,
    editorial_review_threshold: float = 0.59,
) -> go.Figure:
    """Render calibrated risk with a central validation-selected review zone."""

    value = misleading_probability * 100
    lower_boundary = (1 - editorial_review_threshold) * 100
    upper_boundary = editorial_review_threshold * 100
    bar_color = SUCCESS if value < lower_boundary else DANGER if value > upper_boundary else WARNING
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%", "font": {"color": INK, "size": 34, "family": "Georgia"}},
            title={
                "text": "Calibrated misleading-risk probability",
                "font": {"color": SOFT_GREY, "size": 13, "family": "Inter, Arial, sans-serif"},
            },
            gauge={
                "shape": "angular",
                "axis": {
                    "range": [0, 100],
                    "tickcolor": SOFT_GREY,
                    "tickfont": {"color": SOFT_GREY, "size": 10},
                },
                "bar": {"color": bar_color, "thickness": 0.24},
                "bgcolor": PAPER,
                "bordercolor": BORDER,
                "borderwidth": 1,
                "steps": [
                    {"range": [0, lower_boundary], "color": "#E7ECE6"},
                    {"range": [lower_boundary, upper_boundary], "color": "#F1E9DA"},
                    {"range": [upper_boundary, 100], "color": "#F1E2DF"},
                ],
                "threshold": {
                    "line": {"color": "#090909", "width": 3},
                    "thickness": 0.72,
                    "value": upper_boundary,
                },
            },
        )
    )
    return _editorial_layout(
        figure,
        height=275,
        margin={"l": 24, "r": 24, "t": 52, "b": 12},
    )


def feature_contribution_chart(
    explanation: dict[str, list[dict[str, object]]],
) -> go.Figure:
    """Plot local signed term contributions using muted semantic colours."""

    rows: list[dict[str, object]] = []
    for direction, values in explanation.items():
        label = "Toward misleading" if direction == "supports_misleading" else "Toward reliable"
        for value in values:
            rows.append(
                {
                    "Term": value["term"],
                    "Contribution": value["contribution"],
                    "Direction": label,
                }
            )
    if not rows:
        figure = go.Figure()
        figure.add_annotation(
            text="No coefficient-based terms are available for this article.",
            showarrow=False,
            font={"color": SOFT_GREY, "size": 13},
        )
        return _editorial_layout(
            figure,
            height=330,
            margin={"l": 20, "r": 20, "t": 30, "b": 25},
        )
    frame = pd.DataFrame(rows).sort_values("Contribution")
    figure = px.bar(
        frame,
        x="Contribution",
        y="Term",
        color="Direction",
        orientation="h",
        color_discrete_map={"Toward misleading": DANGER, "Toward reliable": SUCCESS},
        labels={"Contribution": "Local TF-IDF × coefficient contribution"},
    )
    figure.update_traces(marker_line_color=PAPER, marker_line_width=0.8)
    figure.update_layout(legend_title_text="")
    return _editorial_layout(
        figure,
        height=430,
        margin={"l": 18, "r": 20, "t": 35, "b": 42},
    )


def model_comparison_chart(frame: pd.DataFrame) -> go.Figure:
    """Compare held-out model metrics with a consistent neutral palette."""

    melted = frame.melt(
        id_vars="model",
        value_vars=["accuracy", "macro_f1", "roc_auc", "pr_auc"],
        var_name="metric",
        value_name="score",
    )
    melted["metric"] = melted["metric"].map(
        {
            "accuracy": "Accuracy",
            "macro_f1": "Macro F1",
            "roc_auc": "ROC AUC",
            "pr_auc": "PR AUC",
        }
    )
    figure = px.bar(
        melted,
        x="model",
        y="score",
        color="metric",
        barmode="group",
        color_discrete_sequence=EDITORIAL_PALETTE,
        labels={"model": "Candidate model", "score": "Held-out score", "metric": "Metric"},
    )
    figure.update_traces(marker_line_color=PAPER, marker_line_width=0.7)
    figure.update_layout(
        yaxis_range=[0, 1.05],
        legend_title_text="",
        bargap=0.24,
        bargroupgap=0.08,
    )
    return _editorial_layout(
        figure,
        height=470,
        margin={"l": 45, "r": 20, "t": 25, "b": 70},
    )


def newsroom_distribution_chart(
    frame: pd.DataFrame,
    *,
    category: str,
    value: str = "Count",
) -> go.Figure:
    """Render a compact privacy-safe aggregate distribution."""

    figure = px.bar(
        frame,
        x=category,
        y=value,
        color=category,
        color_discrete_sequence=EDITORIAL_PALETTE,
        labels={value: "Analyses"},
    )
    figure.update_traces(marker_line_color=PAPER, marker_line_width=0.8, hovertemplate="%{x}: %{y}<extra></extra>")
    figure.update_layout(showlegend=False)
    tick_values = [str(item) for item in frame[category].tolist()]
    figure.update_xaxes(
        tickmode="array",
        tickvals=tick_values,
        ticktext=["<br>".join(textwrap.wrap(item, width=24)) for item in tick_values],
        automargin=True,
    )
    return _editorial_layout(
        figure,
        height=350,
        margin={"l": 44, "r": 20, "t": 20, "b": 110},
    )


def newsroom_activity_chart(frame: pd.DataFrame) -> go.Figure:
    """Render session-local analysis counts over dates where observations exist."""

    figure = px.line(
        frame,
        x="Date",
        y="Analyses",
        markers=True,
        color_discrete_sequence=["#6D5947"],
    )
    figure.update_traces(line={"width": 2.5}, marker={"size": 8})
    return _editorial_layout(
        figure,
        height=330,
        margin={"l": 44, "r": 20, "t": 20, "b": 58},
    )

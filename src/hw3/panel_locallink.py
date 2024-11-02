import os
import panel as pn
import hvplot.pandas
from PIL import Image
import pandas as pd

pn.extension("tabulator")

ACCENT = "teal"

styles = {
    "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
    "border-radius": "4px",
    "padding": "10px",
}

# Extract Data
def get_data():
    return pd.read_excel(os.path.join(os.path.dirname(__file__), 'data', 'kanji_list.xlsx'))

source_data = get_data()

# Calculate key data ranges
stroke_min = int(source_data["Strokes"].min())
stroke_max = int(source_data["Strokes"].max())
Grades = (
    source_data.groupby("Grade").count().sort_values(by='Strokes').iloc[-10:].index.to_list()
)

Grade = pn.widgets.Select(
    name="School year",
    value="1",
    options=sorted(Grades),
    description="The Grade column specifies the grade in which the kanji is taught in Elementary schools in Japan. 7 grade means that it is taught in secondary school.",
)

# Add two sliders for minimum and maximum strokes
min_strokes = pn.widgets.IntSlider(name="Min. Strokes", value=stroke_min, start=stroke_min, end=stroke_max)
max_strokes = pn.widgets.IntSlider(name="Max. Strokes", value=stroke_max, start=stroke_min, end=stroke_max)

def filter_data0(Grade, stroke_min, stroke_max):
    data = source_data[(source_data.Grade == Grade) & (source_data.Strokes >= stroke_min) & (source_data.Strokes <= stroke_max)]
    return data

df0 = pn.rx(filter_data0)(Grade=Grade, stroke_min=stroke_min, stroke_max=stroke_max)
count0 = df0.rx.len()
ingrade_max_strokes = df0.Strokes.max() 
ingrade_min_strokes = df0.Strokes.min() 

def filter_data(Grade, min_strokes, max_strokes):
    data = source_data[(source_data.Grade == Grade) & (source_data.Strokes >= min_strokes) & (source_data.Strokes <= max_strokes)]
    return data

# Create reactive dataframe
df = pn.rx(filter_data)(Grade=Grade, min_strokes=min_strokes, max_strokes=max_strokes)
count = df.rx.len()
avg_strokes = df.Strokes.mean() 

# Plot Data

fig = (
    df[["Strokes", "Grade"]].groupby("Strokes").sum()
).hvplot.bar(
    title="Strokes of Japanese kanji learned by grade",
    rot=90,
    ylabel="number of characters",
    xlabel="Strokes",
    xlim=(0, 30), # min_strokes.value, max_strokes.value
    color=ACCENT,
    width=800,  # Set a fixed width for the plot
    height=400,  # Set a fixed height for the plot
    bar_width=0.9  # Set a fixed width for the bars
)

# Create image pane
image = pn.pane.JPG(os.path.join(os.path.dirname(__file__),'thumbnail.jpg'))

# Create indicators

indicators = pn.Column(
    pn.pane.Markdown("## Grade Information"),
    pn.Row(
        pn.indicators.Number(
            value=count0, 
            name="Total character of this grade", 
            format="{value:,.0f}", 
            styles=styles
        ),
        pn.indicators.Number(
            value=ingrade_max_strokes,
            name="Maximum Strokes in this grade",
            format="{value:,.1f}",
            styles=styles,
        ),
        pn.indicators.Number(
            value=ingrade_min_strokes,
            name="Minimum Strokes in this grade",
            format="{value:,.1f}",
            styles=styles,
        ),
    ),
    pn.pane.Markdown("## <br> in-range Information"),
    pn.Row(
        pn.indicators.Number(
            value=count, 
            name="Count in range", 
            format="{value:,.0f}", 
            styles=styles
        ),
        pn.indicators.Number(
            value=avg_strokes,
            name="Average Strokes in range",
            format="{value:,.1f}",
            styles=styles,
        ),
    )
)

# Create plot and table components
plot = pn.pane.HoloViews(fig, sizing_mode="stretch_both", name="Plot")
table = pn.widgets.Tabulator(df, sizing_mode="stretch_both", name="Table")

# 대시보드 레이아웃 설정
dashboard = pn.Row()

tabs = pn.Tabs(
    plot, table, styles=styles, sizing_mode="stretch_width", height=500, margin=10
)

pn.template.FastListTemplate(
    title="Japanese Kanji Dashboard",
    sidebar=[image, Grade, min_strokes, max_strokes],
    main=[pn.Column(indicators, tabs, sizing_mode="stretch_both")],
    main_layout=None,
    accent=ACCENT,
).servable()

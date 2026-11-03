# Settings by library

The same rules everywhere: one accent, grey for the rest, direct labels, no legend for a single series, no gridlines, zero-based bars, a finding as the title. Colours below are the `paper` theme. Swap them in from `scripts/chart_style.py` for other themes.

```
background #f6f4ef   text #1b1b1b   muted #6f6a61   grey #d8d3c8   accent #d9480f
```

## matplotlib

Use `scripts/chart_style.py`, which already does all of this. If you can't import it, these are the essentials:

```python
import matplotlib.pyplot as plt
plt.rcParams.update({
    "font.size": 14, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.grid": False, "axes.facecolor": "#f6f4ef",
    "figure.facecolor": "#f6f4ef", "text.color": "#1b1b1b", "axes.labelcolor": "#6f6a61",
    "xtick.color": "#6f6a61", "ytick.color": "#1b1b1b",
})
colors = ["#d9480f" if c == highlight else "#d8d3c8" for c in labels]
bars = ax.barh(labels, values, color=colors)
ax.bar_label(bars, padding=4)
ax.set_xticks([])
ax.invert_yaxis()            # largest first
fig.savefig("chart.png", dpi=200, bbox_inches="tight")
```

## Plotly

```python
fig = go.Figure(go.Bar(x=values, y=labels, orientation="h",
                       marker_color=["#d9480f" if l == highlight else "#d8d3c8" for l in labels],
                       text=values, textposition="outside"))
fig.update_layout(showlegend=False, plot_bgcolor="#f6f4ef", paper_bgcolor="#f6f4ef",
                  font=dict(family="Helvetica Neue, Arial", size=15, color="#1b1b1b"),
                  title=dict(text="<b>Google Ads brought 42% of all leads</b>", x=0.02),
                  xaxis=dict(visible=False, rangemode="tozero"),
                  yaxis=dict(autorange="reversed", showgrid=False),
                  margin=dict(l=20, r=40, t=80, b=40))
```

## Chart.js

```js
{
  type: "bar",
  data: { labels, datasets: [{ data: values,
    backgroundColor: labels.map(l => l === highlight ? "#d9480f" : "#d8d3c8") }] },
  options: {
    indexAxis: "y",
    plugins: { legend: { display: false },
               title: { display: true, text: "Google Ads brought 42% of all leads", align: "start" } },
    scales: { x: { beginAtZero: true, display: false, grid: { display: false } },
              y: { grid: { display: false } } }
  }
}
```

Add value labels with the `chartjs-plugin-datalabels` plugin, or draw them in an `afterDatasetsDraw` hook.

## Recharts

```jsx
<BarChart layout="vertical" data={data}>
  <XAxis type="number" hide domain={[0, "dataMax"]} />
  <YAxis type="category" dataKey="name" axisLine={false} tickLine={false} />
  <Bar dataKey="value" label={{ position: "right" }}>
    {data.map(d => <Cell key={d.name} fill={d.name === highlight ? "#d9480f" : "#d8d3c8"} />)}
  </Bar>
</BarChart>
```

Leave out `<Legend />` and `<CartesianGrid />`.

## Vega-Lite

```json
{
  "mark": {"type": "bar"},
  "encoding": {
    "y": {"field": "channel", "type": "nominal", "sort": "-x", "title": null},
    "x": {"field": "leads", "type": "quantitative", "axis": null, "scale": {"zero": true}},
    "color": {"condition": {"test": "datum.channel === 'Google Ads'", "value": "#d9480f"}, "value": "#d8d3c8"}
  },
  "config": {"view": {"stroke": null}, "axis": {"grid": false}}
}
```

## Excel and Google Sheets

You can't set these with code from the agent, so give the user these steps:

1. Insert a **bar** chart (horizontal), not a column chart or pie. Sort the data largest first.
2. Delete the legend and the gridlines, and set the horizontal axis to none.
3. Set every bar's fill to light grey, then click the one bar that matters and colour it the accent.
4. Turn on data labels (Outside End).
5. Replace the chart title with the finding as a sentence.

For an `.xlsx` the agent creates with `openpyxl`, the same settings apply: `chart.legend = None`, gridlines off with `chart.y_axis.majorGridlines = None`, and per-point colours via `DataPoint`.

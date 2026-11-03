# Charts

A slide chart has one job: make the headline's point obvious in two seconds.

## Pick the chart

| The point is about | Use |
| --- | --- |
| One number | The `number` layout, not a chart |
| Change over a few periods (2 to 6) | `bars` |
| Two things compared | `compare` |
| A ranking | `bars`, sorted, largest first |
| Part of a whole | A sentence ("3 of 4 clients…") or `compare`; a pie only with 2 or 3 slices |
| A long trend (12+ points) | A line chart image (see below) |

## Honesty rules

These matter more than looks. A misleading chart, once noticed, discredits the whole deck.

- **Bars start at zero.** In the template, `--v` is the bar height as a percentage of the largest value: `--v = round(value / max × 100)`. Don't stretch small differences to look big. If the difference is small, say so in the title, or show the change as a number.
- **Label the values directly** on the bars. No legend hunting, no gridlines.
- **Highlight one bar**, the one the headline talks about, with `hi`. Leave the rest neutral.
- **Keep the order meaningful:** time runs left to right, and rankings run largest first.
- **No 3D, no shadows, no gradient fills.**
- **State the source and period** in the `source` line.

## Worked example

Values 81, 87, 94. The largest is 94.

- 81 / 94 = 0.862, so `--v: 86`
- 87 / 94 = 0.926, so `--v: 93`
- 94 / 94 = 1, so `--v: 100`

The bars look close because the values are close. That's honest. The headline and the `+13` number slide carry the change.

## Line charts and other chart types

For a long time series or anything the template layouts don't cover, make a chart image and place it with the `image` layout, or as an `<img>` in any layout. For example, use matplotlib with these settings:

```python
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 16, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(11, 4.5), dpi=200)
ax.plot(months, values, color="#d9480f", linewidth=3)   # the theme's --accent
ax.set_ylim(bottom=0)
ax.grid(False)
fig.savefig("chart.png", bbox_inches="tight", transparent=True)
```

Then check it in the rendered slide: are the labels readable at slide size, and does it start at zero?

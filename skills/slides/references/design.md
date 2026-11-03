# Design rules

The template already follows these rules. Read this when you change the template, match a brand, or rebuild a deck in PowerPoint.

## Themes

| Theme | Look | Good for |
| --- | --- | --- |
| `paper` | Warm off-white, near-black text, orange accent | Business reviews, agencies, consulting |
| `swiss` | Pure white, black, red accent | Strategy, design, bold statements |
| `ink` | Near-black background, mint accent | Tech talks, product launches, evening events |
| `forest` | Pale green-grey, deep green accent | Sustainability, health, finance |
| `sand` | Cream, serif headlines, blue accent | Editorial, research, investor updates |
| `mono` | Light grey, monospace, black accent | Developer tools, engineering reviews |

**To match a brand,** change only `--accent` (and `--accent-ink`, the text colour on top of the accent) on the theme. Keep the background and text colours neutral. Brand colours work best as the accent, not the background.

## Colour

- **One accent colour, used for one thing per slide**: the key number, the highlighted bar or the winning option. If everything is highlighted, nothing is.
- Keep backgrounds neutral, off-white or near-black. No gradients.
- Text contrast should be at least 4.5:1. Muted grey text is for labels and sources only.

## Type

- **One font family** (the theme's), with weight and size doing the work. The `sand` theme pairs a serif display face with a sans for body text; that's the maximum.
- **Size scale:** title 68–84 px, headline 50–64 px, body 22–28 px, labels 18 px, sources 15 px. Nothing below 15 px: the back row can't read it.
- Sentence case everywhere. Uppercase only for small kicker labels, with letter spacing.
- No text shadows, outlines or glow.

## Layout

- **Left-align text.** Centred text is harder to read and is the default AI look. Centre only a single statement or a quote.
- Use generous margins (88 px left and right in the template) and keep them the same on every slide, so the deck feels steady when you click through.
- **Use empty space.** A slide that's 60% empty looks confident; a full slide looks anxious.
- Anchor content to the bottom or top, not floating in the middle of a card.

## The AI-deck look, and why each part fails

| Pattern | Why it fails | Do instead |
| --- | --- | --- |
| Purple/blue gradient background | It's the default of every AI slide tool, so it signals "generated" instantly | Neutral background, one accent |
| Frosted-glass card holding the content | Adds a box with no meaning and lowers contrast | Put the content on the slide directly |
| Emoji bullets 🚀💡📈 | Decoration pretending to be meaning | A layout that shows the structure |
| Centred everything | Slower to read; no visual anchor | Left-align; centre one statement at most |
| Title Case Topic Titles | Names a subject but makes no point | A sentence-case claim |
| Six bullets per slide | Nobody reads them while you talk | One point; detail in notes |
| Stock icons by every line | Visual noise, same icons as every other deck | Nothing, or one real image |
| 3D and exploded pie charts | Distort the values | Flat bars that start at zero |
| "Thank you! Questions?" | Wastes the last thing people see | The ask, the owner and the date |

## Images

Use real screenshots, product photos or photos of real people (with permission). If there's no real image, use no image: a number or a statement is stronger than stock art. Make images fill their area, as in the `image` layout, rather than floating with a border.

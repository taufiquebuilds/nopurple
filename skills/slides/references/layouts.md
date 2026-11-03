# Layouts

Each layout is a class on `<section class="slide LAYOUT">` in `templates/deck.html`. Pick by the slide's job, not by habit. Every snippet below is complete: paste it in and change the text.

A `kicker` (small label above the title) is optional on every layout. Use it to name the topic, so the title can carry the point.

## title: the opening slide

The conclusion in plain words, not just the deck's subject.

```html
<section class="slide title">
  <div class="bar"></div>
  <p class="kicker">Q3 review · Acme Studio</p>
  <h1>Retention is our growth engine now</h1>
  <p>What changed in Q3, and what we do next</p>
</section>
```

## statement: one idea, nothing else

For a turning point, a principle or a provocative claim. Fifteen words at most.

```html
<section class="slide statement">
  <h2>We don't have a lead problem. We have a <em>follow-up</em> problem.</h2>
</section>
```

## section: chapter divider

Use it only in decks over about 12 slides. It fills with the accent colour.

```html
<section class="slide section">
  <p class="kicker">Part 2</p>
  <h1>The plan</h1>
</section>
```

## number: one fact that matters

The big number is the evidence, so don't repeat the headline's number. Show the change or the comparison.

```html
<section class="slide number">
  <p class="kicker">Client retention</p>
  <h2>We kept <em>94%</em> of clients this quarter, up from 81%.</h2>
  <div class="row">
    <div class="big">+13</div>
    <p>points of retention since Q1, after monthly strategy calls began in July.</p>
  </div>
  <div class="source">Source: CRM, Jan–Sep</div>
</section>
```

## kpis: several numbers at a glance

For a monthly report or dashboard summary: 2 to 4 cards (`--n` sets how many), each with the value, what it was before and the change. Mark at most one card `hi`, the one the headline is about. Don't use this to avoid choosing: if one number matters most, use `number` instead.

```html
<section class="slide kpis" style="--n: 4">
  <p class="kicker">October at a glance</p>
  <h2>Every headline number improved on September</h2>
  <div class="cards">
    <div class="card hi"><h3>New patient bookings</h3><div class="v">41</div><div class="was">September: 29</div><span class="d">+41%</span></div>
    <div class="card"><h3>Calls from Google profile</h3><div class="v">86</div><div class="was">September: 54</div><span class="d">+59%</span></div>
    <div class="card"><h3>Cost per lead</h3><div class="v">$18</div><div class="was">September: $31</div><span class="d">42% cheaper</span></div>
    <div class="card"><h3>Website visits</h3><div class="v">4,200</div><div class="was">September: 3,100</div><span class="d">+35%</span></div>
  </div>
</section>
```

## bars: change over time, or a ranking

2 to 6 bars. `--v` is each bar's height as a percentage of the **largest** value, so bars start at zero and stay proportional: `--v = value / max × 100`. Highlight one bar with `hi`. See `charts.md`.

```html
<section class="slide bars">
  <p class="kicker">Retention by quarter</p>
  <h2>The jump came the quarter the calls started</h2>
  <div class="chart">
    <div class="b" style="--v: 86"><b>81%</b><i></i><span>Q1</span></div>
    <div class="b" style="--v: 93"><b>87%</b><i></i><span>Q2</span></div>
    <div class="b hi" style="--v: 100"><b>94%</b><i></i><span>Q3 · calls began</span></div>
  </div>
  <div class="source">Bars start at zero.</div>
</section>
```

## compare: two options, before and after, us versus them

Mark the winner with `hi`. Keep each side to one number and one line.

```html
<section class="slide compare">
  <p class="kicker">Cost of churn</p>
  <h2>Keeping a client costs a fifth of winning a new one</h2>
  <div class="cols">
    <div class="col"><h3>Win a new client</h3><div class="v">$4,800</div><p>Ads, pitch work and onboarding</p></div>
    <div class="col hi"><h3>Keep a client</h3><div class="v">$950</div><p>Twelve strategy calls a year</p></div>
  </div>
</section>
```

## steps: a plan or a process

3 or 4 steps (`--n` sets the column count). Each step has a bold action and one line.

```html
<section class="slide steps" style="--n: 3">
  <p class="kicker">Q4 plan</p>
  <h2>Three moves to reach 96% by March</h2>
  <ol>
    <li><strong>Calls for every client</strong>Extend monthly calls to the 30 smaller accounts.</li>
    <li><strong>Flag risk early</strong>Review any client with two missed calls within a week.</li>
    <li><strong>Report the value</strong>Send a one-page results note after each call.</li>
  </ol>
</section>
```

## quote: proof from a real person

Use a real quote only, attributed by role if there's no permission to use a name. Never invent one.

```html
<section class="slide quote">
  <blockquote>The call is the only meeting in my month where someone tells me what to do next.</blockquote>
  <cite>Operations lead, retained client</cite>
</section>
```

## image: a product shot, screenshot or photo

The image fills the right half. Use a real screenshot or photo, not stock clip art.

```html
<section class="slide image">
  <div class="text">
    <p class="kicker">The product</p>
    <h2>One screen shows every client's health</h2>
    <p>Red means two missed calls. The account lead gets a nudge the same day.</p>
  </div>
  <figure><img src="screenshot.png" alt="Client health dashboard"></figure>
</section>
```

## closing: the ask

End on the decision, the owner and the date. Never "Thank you".

```html
<section class="slide closing">
  <p class="kicker">Decision needed</p>
  <h2>Approve one extra strategist for Q4 so every client gets a monthly call.</h2>
  <div class="ask">Approve by 15 November</div>
</section>
```

## Speaker notes

Add notes inside any slide. They stay out of the rendered slide and out of the slop check's word count:

```html
<aside class="notes">Retention figure is from the CRM export on 30 Sep; excludes two clients who closed their business.</aside>
```

(The template hides `.notes`. If you add your own CSS, keep `.notes { display: none; }`.)

## When bullets are right

A short list of parallel items, like requirements or features, can be bullets. Keep 3 to 5, under 8 words each, with no emoji, using a plain `<ul>` inside any layout.

---
name: shiny-python-dashboard
description: Best practices for building dashboards in Shiny for Python, covering both Core and Express APIs. Use when building, reviewing, or refactoring Shiny for Python apps including dashboards, sidebar layouts, multi-page navigation, value boxes, reactive filtering, plotly/seaborn charts, data tables, styled card layouts, faicons icons, and interactive maps. Triggers on shiny for python, shiny dashboard, shiny core vs express, page_sidebar, page_navbar, value_box, navset, nav_panel, reactive calc, render_plotly, render.data_frame, sidebar layout, navigation panels, faicons, icon_svg, ipyleaflet, map.
---

# Shiny for Python Dashboard Best Practices

Patterns extracted from production templates: `dashboard-tips`, `nba-dashboard`, `stock-app`,
`basic-navigation`, `basic-sidebar`, and `map-distance`.

## Project structure

```
my-dashboard/
├── app-core.py          # Core API version
├── app-express.py       # Express API version
├── shared.py            # Data loading, constants, app_dir
├── plots.py             # (optional) Complex chart functions
├── styles.css           # Minimal CSS overrides
├── data.csv             # Static data files
└── requirements.txt
```

`shared.py` always exports `app_dir = Path(__file__).parent` and pre-loaded data.
Extract chart functions exceeding ~15 lines into `plots.py`.

## Quick start — minimal Core dashboard

```python
from shared import app_dir, df
from shiny import App, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(ui.input_select("var", "Variable", choices=["col_a", "col_b"])),
    ui.card(ui.card_header("Plot"), ui.output_plot("plot"), full_screen=True),
    ui.include_css(app_dir / "styles.css"),
    title="Dashboard", fillable=True,
)

def server(input, output, session):
    @reactive.calc
    def filtered(): return df[df["col"] == input.var()]

    @render.plot
    def plot(): ...

app = App(app_ui, server)
```

## Quick start — minimal Express dashboard

```python
from shared import df
from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(title="Dashboard", fillable=True)
with ui.sidebar():
    ui.input_select("var", "Variable", choices=["col_a", "col_b"])

with ui.card(full_screen=True):
    ui.card_header("Plot")
    @render.plot
    def plot(): ...

@reactive.calc
def filtered(): return df[df["col"] == input.var()]
```

## Detailed reference guides

Read these files for in-depth patterns and examples on specific topics:

**Layout, sidebar, and navigation**: See [references/layout-and-navigation.md](references/layout-and-navigation.md)
- `page_sidebar` vs `page_navbar` selection, sidebar input patterns, `open="desktop"`,
  `navset_card_underline` with footer, two-level navigation hierarchy, `nav_spacer`

**Value boxes, cards, and grid layout**: See [references/components.md](references/components.md)
- Value box rows with `fill=False`, `faicons` showcase icons, dynamic icons with `ui.hold()`,
  card patterns, `col_widths`, responsive breakpoints, popovers and inline controls in card headers

**Reactivity and rendering**: See [references/reactivity-and-rendering.md](references/reactivity-and-rendering.md)
- `@reactive.calc` chains, `@reactive.effect` + `@reactive.event`, `req()`, `@render_plotly`,
  `@render.plot`, `@render.data_frame`, interactive Plotly click events, value box content rendering

**Styling and data loading**: See [references/styling-and-data.md](references/styling-and-data.md)
- CSS inclusion, `--bslib-sidebar-main-bg`, hiding Plotly modebar, popover theming,
  static CSV vs live API data loading, Pandas vs Polars filtering patterns

**Icons and interactive maps**: See [references/icons-and-maps.md](references/icons-and-maps.md)
- `faicons` import patterns (namespace vs direct), icon dictionary, dynamic conditional icons,
  icons as popover triggers, common icon reference table, `ipyleaflet` map rendering via
  `shinywidgets`, basemap switching, draggable markers with input sync, partial layer updates,
  geopy distance calculations, value box theme gradients

**Core vs Express comparison**: See [references/core-vs-express.md](references/core-vs-express.md)
- Side-by-side comparison table, import differences, UI construction, server function
  vs module-level reactivity, output placement, `@render.express` vs `@render.ui`

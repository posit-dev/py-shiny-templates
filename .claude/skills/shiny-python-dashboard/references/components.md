# Value Boxes, Cards, and Grid Layout

## Contents

- Value boxes
- Dynamic showcase icons
- Standard card pattern
- Grid layout with col_widths
- Card headers with inline controls

---

## Value boxes

Always render value boxes in a row with `fill=False` to prevent vertical stretching.

```python
# Core
ui.layout_columns(
    ui.value_box("Total tippers", ui.output_ui("total_tippers"),
        showcase=icon_svg("user", "regular")),
    ui.value_box("Average tip", ui.output_ui("average_tip"),
        showcase=icon_svg("wallet")),
    ui.value_box("Average bill", ui.output_ui("average_bill"),
        showcase=icon_svg("dollar-sign")),
    fill=False,
)
```

```python
# Express
with ui.layout_columns(fill=False):
    with ui.value_box(showcase=icon_svg("user", "regular")):
        "Total tippers"
        @render.express
        def total_tippers():
            tips_data().height

    with ui.value_box(showcase=icon_svg("wallet")):
        "Average tip"
        @render.express
        def average_tip():
            d = tips_data().select((pl.col("tip") / pl.col("total_bill")).mean()).item()
            f"{d:.1%}" if d else "N/A"
```

Use `faicons.icon_svg()` for the `showcase` parameter. Common icons:
`"user"`, `"wallet"`, `"dollar-sign"`, `"percent"`, `"ellipsis"`.

`ui.layout_column_wrap(fill=False)` is an alternative to `ui.layout_columns(fill=False)` —
both work for value box rows.

---

## Dynamic showcase icons

Render a conditional icon (e.g., up/down arrow) via `@render.ui` and pass
`ui.output_ui("change_icon")` as the `showcase` parameter:

```python
# Core — dynamic showcase
ui.value_box("Change", ui.output_ui("change"), showcase=ui.output_ui("change_icon"))

@render.ui
def change_icon():
    icon = icon_svg("arrow-up" if get_change() >= 0 else "arrow-down")
    icon.add_class(f"text-{'success' if get_change() >= 0 else 'danger'}")
    return icon
```

In Express, use `with ui.hold():` when an output is referenced **before** it is defined:

```python
# Express — forward-referenced output
with ui.value_box(showcase=output_ui("change_icon")):
    "Change"
    @render.ui
    def change(): return f"${get_change():.2f}"

# Define the forward-referenced output after the widget that uses it
with ui.hold():
    @render.ui
    def change_icon():
        icon = icon_svg("arrow-up" if get_change() >= 0 else "arrow-down")
        icon.add_class(f"text-{'success' if get_change() >= 0 else 'danger'}")
        return icon
```

---

## Standard card pattern

```python
# Core
ui.card(
    ui.card_header("Price history"),
    output_widget("price_history"),
    full_screen=True,
)
```

```python
# Express
with ui.card(full_screen=True):
    ui.card_header("Price history")
    @render_plotly
    def price_history(): ...
```

Use `ui.card_footer()` for supplementary text below the card content:

```python
ui.card_footer("Percentiles are based on career per game averages.")
```

---

## Grid layout with col_widths

Use `ui.layout_columns(col_widths=[...])` for asymmetric card arrangements:

```python
ui.layout_columns(
    card_a, card_b, card_c,
    col_widths=[6, 6, 12],  # two cards on top row, one full-width below
)
```

For responsive breakpoints, pass a dict:

```python
col_widths={"sm": 12, "md": 12, "lg": [4, 8]}
```

This stacks cards vertically on small/medium screens and splits 4:8 on large screens.

---

## Card headers with inline controls

Use flexbox classes for alignment.

### Popover with secondary inputs

```python
ui.card_header(
    "Total bill vs tip",
    ui.popover(
        icon_svg("ellipsis"),
        ui.input_radio_buttons("color_var", None, ["none", "sex", "day"], inline=True),
        title="Add a color variable",
        placement="top",
    ),
    class_="d-flex justify-content-between align-items-center",
)
```

### Inline select dropdown

```python
ui.card_header(
    "Player career ",
    ui.input_select("stat", None, choices=stats, selected="PTS", width="auto"),
    " vs the rest of the league",
    class_="d-flex align-items-center gap-1",
)
```

Use `"d-flex justify-content-between align-items-center"` when the control should be
pushed to the far right. Use `"d-flex align-items-center gap-1"` when the control
is inline within the title text.

# NBA Dashboard

This template shows how to build a dashbord based on an external API. Some things to note:

1. We use a `ui.output_ui` to generate a select input which only has players from a given team
2. The value boxes are generated using a module, which makes it a bit easier to include sparkline plots in the value boxes.
3. The plots are drawn using plotly, which means that we use the shinywidgets package instead of `@render.plot`

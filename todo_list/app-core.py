from htmltools import css

from shiny import App, module, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text("todo_input_text", "", placeholder="Todo text"),
        ui.input_action_button("add", "Add to-do", class_="btn btn-primary"),
    ),
    ui.output_text("cleared_tasks"),
    ui.div(id="tasks"),
    title="Shiny TodoMVC",
)


def server(input, output, session):
    finished_tasks = reactive.Value(0)
    task_counter = reactive.Value(0)

    # Passing an iterate counter callback down to the module is a simple way
    # to manipulate application state from inside of a module
    def iterate_counter():
        finished_tasks.set(finished_tasks.get() + 1)

    @render.text
    def cleared_tasks():
        return f"Finished tasks: {finished_tasks()}"

    @reactive.Effect
    @reactive.event(input.add)
    def add():
        counter = task_counter.get() + 1
        task_counter.set(counter)
        id = "task_" + str(counter)
        ui.insert_ui(
            selector="#tasks",
            where="beforeEnd",
            ui=task_ui(id),
        )

        task_server(id, text=input.todo_input_text(), on_finish=iterate_counter)

        ui.update_text("todo_input_text", value="")


# Modules to define the rows


@module.ui
def task_ui():
    return ui.output_ui("button_row")


@module.server
def task_server(input, output, session, text, on_finish):
    finished = reactive.Value(False)

    @render.ui
    def button_row():
        button = None
        if finished():
            button = ui.input_action_button("clear", "Clear", class_="btn btn-warning")
        else:
            button = ui.input_action_button(
                "finish", "Finish", class_="btn btn-primary"
            )

        return ui.layout_columns(
            ui.column(4, button),
            ui.column(8, text),
            class_="mt-3 p-3 border align-items-center",
            style=css(text_decoration="line-through" if finished() else None),
            col_widths=[2, 10],
        )

    @reactive.Effect
    @reactive.event(input.finish)
    def finish_task():
        finished.set(True)
        # We call the on_finish function to increment the finished tasks counter at the application level
        on_finish()

    @reactive.Effect
    @reactive.event(input.clear)
    def clear_task():
        ui.remove_ui(selector=f"div#{session.ns('button_row')}")

        # Since remove_ui only removes the HTML the reactive effects will be held
        # in memory unless they're explicitly destroyed. This isn't a big
        # deal because they're very small, but it's good to clean them up.
        finish_task.destroy()
        clear_task.destroy()


app = App(app_ui, server)

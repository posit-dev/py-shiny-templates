# By Chelsea Parlett Pelleriti
import matplotlib.pyplot as plt

# Import modules for modeling
import pandas as pd
import seaborn as sns
from compare import compare, sim_data

# Import helper functions from local modules
from shared import mathjax, prose, restrict_width
from shiny import App, reactive, render, ui

# Define the UI
app_ui = ui.page_fixed(
    mathjax,
    restrict_width(
        ui.h1(
            "How Does Regularization Strength Affect Coefficient Estimates?",
            class_="text-lg-center text-left",
        ),
        sm=10,
        md=10,
        lg=8,
    ),
    restrict_width(
        ui.input_slider(
            "a",
            "Select a Regularization Strength:",
            0.000000001,
            1,
            0.1,
            step=0.01,
            width="100%",
        ),
        ui.p(
            {"class": "pt-4 small"},
            "(Notice how, as the strength increases, lasso coefficients approach 0)",
        ),
        sm=10,
        md=7,
        lg=5,
        pad_y=4,
    ),
    restrict_width(ui.output_plot("plot"), lg=11),
    # Explanation and Explore prose
    restrict_width(prose, sm=10, md=10, lg=6),
    restrict_width(
        ui.h2("Plots Separated by Vowels and Consonants", class_="text-center"), lg=11
    ),
    # output plots separated by real effects (vowels), and zero-effects (consonants)
    restrict_width(
        ui.output_plot("plotVOWELS"),
        ui.output_plot("plotCONSONANTS"),
        lg=11,
        pad_y=0,
    ),
    ui.div(class_="pb-5"),  # add padding to bottom of page
)


def server(input, output, session):
    # data
    nsims = 100
    sim = [sim_data(n=1000) for i in range(0, nsims)]

    # reactive Calc that runs LASSO, Ridge, and Linear models on generated data
    @reactive.calc
    def models():
        sim_alpha = [compare(df, alpha=input.a()) for df in sim]
        sim_alpha = pd.concat(sim_alpha)

        return sim_alpha

    # output plot of all simulation coefficients
    @render.plot
    def plot():
        # get data from reactive Calc
        sim_alpha = models()

        # create plot and manage aesthetics
        fig, ax = plt.subplots()
        ax2 = sns.boxplot(
            x="conames",
            y="coefs",
            hue="model",
            data=sim_alpha,
            ax=ax,
            order=[
                "A",
                "E",
                "I",
                "O",
                "U",
                "Y",
                "W",
                "B",
                "C",
                "D",
                "G",
                "H",
                "J",
                "K",
            ],
        )
        tt = "Coefficient Estimates when alpha = " + str(input.a())
        ax2.set(xlabel="", ylabel="Coefficient Value", title=tt)
        return fig

    # output plot of all simulation coefficients (vowels only)
    @render.plot
    def plotVOWELS():
        # get data from reactive Calc
        sim_alpha = models()
        vowels = [n in ["A", "E", "I", "O", "U", "Y", "W"] for n in sim_alpha.conames]
        sim_alpha_V = sim_alpha.loc[vowels]

        # create plot and manage aesthetics
        fig, ax = plt.subplots()
        ax2 = sns.boxplot(
            x="conames",
            y="coefs",
            hue="model",
            data=sim_alpha_V,
            ax=ax,
            order=["A", "E", "I", "O", "U", "Y", "W"],
        )
        tt = "VOWEL Coefficient Estimates when alpha = " + str(input.a())
        ax2.set(xlabel="", ylabel="Coefficient Value", title=tt)
        return fig

    # output plot of all simulation coefficients (consonants only)
    @render.plot
    def plotCONSONANTS():
        # get data from reactive Calc
        sim_alpha = models()

        consonants = [
            n in ["B", "C", "D", "G", "H", "J", "K"] for n in sim_alpha.conames
        ]
        sim_alpha_C = sim_alpha.loc[consonants]

        # create plot and manage aesthetics
        fig, ax = plt.subplots()
        ax2 = sns.boxplot(
            x="conames",
            y="coefs",
            hue="model",
            data=sim_alpha_C,
            ax=ax,
            order=["B", "C", "D", "G", "H", "J", "K"],
        )
        tt = "CONSONANT Coefficient Estimates when alpha = " + str(input.a())
        ax2.set(xlabel="", ylabel="Coefficient Value", title=tt)
        return fig


app = App(app_ui, server)

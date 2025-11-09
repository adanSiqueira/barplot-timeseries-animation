import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process
import pandas as pd
import seaborn as sns
import numpy as np

def setup_plotstyle(ax: plt.Axes) -> None:
    """
    Apply a clean and minimalistic visual style to a Matplotlib Axes object.

    This function customizes the given axes to remove unnecessary spines,
    hide redundant tick marks, and apply Seaborn’s "whitegrid" style. 
    It is intended to make visualizations cleaner and easier to read.

    Parameters:
    ax : plt.Axes
        The Matplotlib axes object to apply the style to.

    Returns: None
    """
    sns.set_style("whitegrid")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('none')
    ax.tick_params(axis='x', which='both', bottom=False, top=False)
    ax.tick_params(axis='y', which='both', left=False, right=False)


def setup_year(ax: plt.Axes, year: int) -> None:
    """
    Display the current year as a label on the animation plot, placing a year label inside the plot area,
    aligned to the bottom-right corner of the chart.

    Parameters:
    ax : plt.Axes
        The Matplotlib axes object to annotate.
    year : int
        The year (or any numeric frame identifier) to display.

    Returns: None
    """
    ax.text(0.9, 0.05, str(year), transform=ax.transAxes,
            ha='center', color="#0B0101", fontsize=15)


def save_animation(df: pd.DataFrame, frames: list | np.ndarray) -> None:
    """
    Generate and save a bar chart time series animation as an MP4 file.

    For each frame (each year), the function selects the top 10 entities
    based on a numeric column ('TPopulation1Jan') and animates their evolution
    over time. The animation is saved using the 'ffmpeg' writer.

    Parameters:
    df : pd.DataFrame
        A DataFrame containing at least the following columns:
        - 'Time': used to determine frames.
        - 'Location': categorical variable (e.g., country names).
        - 'TPopulation1Jan': numeric variable to visualize.
    frames : list | np.ndarray
        A list or array of frame identifiers (e.g., years).

    Returns: None
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    def animate(frame):
        ax.clear()
        pop_data_frame = df[df['Time'] == frame]
        top_countries = pop_data_frame.nlargest(10, 'TPopulation1Jan')
        sns.barplot(
            x='TPopulation1Jan', y='Location', data=top_countries,
            hue='Location', legend=False, palette='viridis', ax=ax
        )
        for i, row in top_countries.iterrows():
            ax.text(row['TPopulation1Jan'], row['Location'],
                    f'{row["TPopulation1Jan"]:.2f}', va='center', color='black')

        ax.set_title(f"Top 10 Populations - {frame}")
        return []

    anim = FuncAnimation(fig, animate, frames=frames, interval=200)
    print("Saving animation as mp4...")
    anim.save("animation.mp4", writer="ffmpeg", fps=5)
    print("Animation saved as animation.mp4")


def show_animation(df: pd.DataFrame, frames: list | np.ndarray) -> None:
    """
    Display an interactive time series bar chart animation.

    This function creates and shows an animated barplot directly in the UI. It is useful for previewing before exporting.

    Parameters:
    df : pd.DataFrame
        A DataFrame containing at least the following columns:
        - 'Time': used to determine frames.
        - 'Location': categorical variable (e.g., country names).
        - 'TPopulation1Jan': numeric variable to visualize.
    frames : list | np.ndarray
        A list or array of frame identifiers (e.g., years).

    Returns: None
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    def animate(frame):
        ax.clear()
        setup_plotstyle(ax)
        setup_year(ax, frame)
        pop_data_frame = df[df['Time'] == frame]
        top_countries = pop_data_frame.nlargest(10, 'TPopulation1Jan')
        sns.barplot(
            x='TPopulation1Jan', y='Location', data=top_countries,
            hue='Location', legend=False, palette='viridis', ax=ax
        )
        for i, row in top_countries.iterrows():
            ax.text(row['TPopulation1Jan'], row['Location'],
                    f'{row["TPopulation1Jan"]:.2f}', va='center', color='black')
        ax.set_title(f"Top 10 Populations - {frame}")
        return []

    anim = FuncAnimation(fig, animate, frames=frames, interval=200)
    plt.show()


if __name__ == "__main__":
    pop_data = pd.read_csv('./data/clean-data.csv')
    frames = pop_data['Time'].unique().tolist()

    # Start saving in a background process
    p = Process(target=save_animation, args=(pop_data, frames))
    p.start()

    # Show animation in main thread
    show_animation(pop_data, frames)

    p.join()

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from multiprocessing import Process
import pandas as pd
import seaborn as sns
import numpy as np
import textwrap
from PIL import Image
import os

def setup_plotstyle(ax: plt.Axes) -> None:
    """Apply a clean and minimalistic visual style to a Matplotlib Axes object."""
    sns.set_style("whitegrid")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('none')
    ax.tick_params(axis='x', which='both', bottom=False, top=False)
    ax.tick_params(axis='y', which='both', left=False, right=False)

def wrap_labels(ax: plt.Axes, width: int|float = 12) -> None:
    """Wrap y-axis tick labels to a given character width.
    
    Parameters
    ----------
    ax : plt.Axes
        The plot axes containing the bars.
    width : int|float
        The maximum character width for wrapping labels.
        
    Returns: None
    """
    labels = [t.get_text() for t in ax.get_yticklabels()]
    wrapped_labels = [textwrap.fill(label, width) for label in labels]
    ax.set_yticklabels(wrapped_labels)

def setup_dt(ax: plt.Axes, dt: int) -> None:
    """Display the current dt (frame label) on the chart.
    
    Parameters
    ----------
    ax : plt.Axes
        The plot axes containing the bars.
    dt : int
        The current frame label (e.g., year).
        
    Returns: None
    """
    ax.text(0.9, 0.05, str(dt), transform=ax.transAxes,
            ha='center', color="#0B0101", fontsize=15)

def load_icons(df: pd.DataFrame, icon_folder: str, label_col: str) -> dict:
    """
    Load and resize icons for each label in the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing a column with unique labels.
    icon_folder : str
        Path to the folder containing icons (e.g., './icons').
    label_col : str
        The column name containing labels that match icon filenames.

    Returns
    -------
    dict
        A dictionary mapping label → PIL Image.
    """
    icons = {}
    for label in df[label_col].unique():
        filename = os.path.join(icon_folder, f"{label}.png")
        if os.path.exists(filename):
            img = Image.open(filename).convert("RGB")
            img.thumbnail((30, 20), Image.Resampling.LANCZOS)
            icons[label] = img
    return icons

def add_icons(ax: plt.Axes, data: pd.DataFrame, icons: dict) -> None:
    """
    Attach country flags right after each label in the horizontal bar chart.

    Parameters
    ----------
    ax : plt.Axes
        The plot axes containing the bars.
    data : pd.DataFrame
        The DataFrame for the current frame (e.g., top 10 items).
    icons : dict
        A dictionary mapping label → PIL Image.
    """
    # Retrieve y-tick labels (they match the data['label'] order)
    ytick_labels = [t.get_text().replace('\n', ' ') for t in ax.get_yticklabels()]
    ytick_positions = ax.get_yticks()

    for y_pos, label in zip(ytick_positions, ytick_labels):
        if label in icons:
            img = icons[label]
            imagebox = OffsetImage(img, zoom=0.45)
            ab = AnnotationBbox(
                imagebox,
                xy=(0, y_pos),
                xybox=(-15, 0),
                box_alignment=(0, 0.5),
                frameon=False,
                xycoords=('data', 'data'),
                boxcoords="offset points",
                pad=0
            )
            ax.add_artist(ab)

def save_animation(df: pd.DataFrame, frames: list | np.ndarray, icons: dict) -> None:
    """
    Generate and save a bar chart dt series animation as an MP4 file.

    For each frame (each dt), the function selects the top 10 entities
    based on a numeric column ('x') and animates their evolution
    over dt. The animation is saved using the 'ffmpeg' writer.

    Parameters:
    df : pd.DataFrame
        A DataFrame containing at least the following columns:
        - 'dt': used to determine frames.
        - 'label': categorical variable (e.g., country names).
        - 'x': numeric variable to visualize.
    frames : list | np.ndarray
        A list or array of frame identifiers (e.g., years).
    icons : dict
        A dictionary mapping label → PIL Image for icons.

    Returns: None
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    def animate(frame):
        ax.clear()
        setup_plotstyle(ax)
        setup_dt(ax, frame)
        frame_data = df[df['dt'] == frame]
        top_items = frame_data.nlargest(10, 'x')
        sns.barplot(
            x='x', y='label', data=top_items,
            hue='label', legend=False, palette='viridis', ax=ax
        )
        wrap_labels(ax, width=18)
        for label in ax.get_yticklabels():
            label.set_ha('right')
            label.set_x(-0.014)
            label.set_fontweight('bold')
        for _, row in top_items.iterrows():
            ax.text(row['x'], row['label'], f'{row["x"]:.2f}',
                    va='center', color='black')
        add_icons(ax, top_items, icons)
        ax.set_title(f"Top 10 Entities - {frame}")
        return []

    anim = FuncAnimation(fig, animate, frames=frames, interval=200)
    print("Saving animation as mp4...")
    anim.save("animation.mp4", writer="ffmpeg", fps=5)
    print("Animation saved as animation.mp4")


def show_animation(df: pd.DataFrame, frames: list | np.ndarray, icons: dict) -> None:
    """Display an animated time series bar chart with optional icons.
    Parameters:
    ----------
    df : pd.DataFrame
        A DataFrame containing at least the following columns:
        - 'dt': used to determine frames.
        - 'label': categorical variable (e.g., country names).
        - 'x': numeric variable to visualize.
    frames : list | np.ndarray
        A list or array of frame identifiers (e.g., years).
    icons : dict
        A dictionary mapping label → PIL Image for icons.
    
    Returns: None
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    def animate(frame):
        ax.clear()
        setup_plotstyle(ax)
        setup_dt(ax, frame)
        frame_data = df[df['dt'] == frame]
        top_items = frame_data.nlargest(10, 'x')
        sns.barplot(
            x='x', y='label', data=top_items,
            hue='label', legend=False, palette='rocket', ax=ax
        )
        wrap_labels(ax, width=18)
        for label in ax.get_yticklabels():
            label.set_ha('right')
            label.set_x(-0.014)
            label.set_fontweight('bold')
        for _, row in top_items.iterrows():
            ax.text(row['x'], row['label'], f'{row["x"]:.2f}',
                    va='center', color='black')
        add_icons(ax, top_items, icons)
        ax.set_title(f"Top 10 Entities - {frame}")
        return []

    anim = FuncAnimation(fig, animate, frames=frames, interval=200)
    plt.show()


if __name__ == "__main__":
    pop_data = pd.read_csv('./data/clean-formatted-data.csv')
    frames = pop_data['dt'].unique().tolist()

    # Load icons once
    icons = load_icons(pop_data, './icons', label_col='label')

    # Start saving in background if desired
    p = Process(target=save_animation, args=(pop_data, frames, icons))
    p.start()
    show_animation(pop_data, frames, icons)
    p.join()

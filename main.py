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

def add_icons(ax: plt.Axes, icons: dict) -> None:
    """
    Attach country flags right after each label in the horizontal bar chart.

    Parameters
    ----------
    ax : plt.Axes
        The plot axes containing the bars.
    icons : dict
        A dictionary mapping label → PIL Image.
    """
    # Retrieve y-tick labels from the axes
    ytick_labels = [t.get_text().replace('\n', ' ') for t in ax.get_yticklabels()]
    ytick_positions = ax.get_yticks()

    for y_pos, label in zip(ytick_positions, ytick_labels):
        if label in icons:
            img = icons[label].convert("RGBA")

            # Adjusting zoom manually: 
                # imagebox = OffsetImage(img, zoom=0.45)

            # Adjust zoom dynamically:
            fig = ax.get_figure()
            dpi_scale = fig.dpi / 100.0  # Normalize to standard 100 dpi
            imagebox = OffsetImage(img, zoom=0.07 / dpi_scale) # set zoom=0.6 if "__name__" == "__main__"

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
            
def draw_frame(ax: plt.Axes, df: pd.DataFrame, title: str, frame: int, icons: dict, n_largest: int = 10, colors: list | None = None, palette: str| None = 'viridis') -> None:
    """Draw a single frame of the animation.
    
    Parameters
    ----------
    ax : plt.Axes
        The plot axes containing the bars.
    df : pd.DataFrame
        The DataFrame for the current frame (e.g., top 10 items).
    title : str
        The title of the frame.
    frame : int
        The current frame label (e.g., year).
    icons : dict
        A dictionary mapping label → PIL Image for icons.
    colors : list | None
        A list of colors for the bars. If None, the palette will be used.
    palette : str
        The color map palette to use.
        
    Returns: None
    """
    ax.clear()
    setup_plotstyle(ax)
    setup_dt(ax, frame)
    frame_data = df[df['dt'] == frame]
    top_items = frame_data.nlargest(n_largest, 'x')

    if colors is not None:  # explicit colors
        bars = ax.barh(y=top_items['label'], width=top_items['x'], color=colors, edgecolor='none')
    else:  # use palette
        sns.barplot(x='x', y='label', data=top_items, hue='label', legend=False, palette=palette, ax=ax)

    wrap_labels(ax, width=18)
    for label in ax.get_yticklabels():
        label.set_ha('right')
        label.set_x(-0.014)
        label.set_fontweight('bold')
    for _, row in top_items.iterrows():
        ax.text(row['x'], row['label'], f'{row["x"]:.2f}', va='center', color='black')
    add_icons(ax, icons)
    # Hide axis labels
    ax.set_xlabel('')
    ax.set_ylabel('')
    # Set title with larger font size and bold
    ax.set_title(f"{title}", fontsize=18, fontweight='bold')

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

def save_animation(df: pd.DataFrame, 
    frames: list | np.ndarray | pd.Series, 
    icons: dict,
    output_path: str = os.path.dirname(os.path.abspath(__file__)),
    title: str = None, 
    width: int|float = 12, 
    height: int|float = 6,
    fps: int = 10, 
    n_largest: int = 10, 
    palette: str| None = 'viridis') -> None:
    """
    Generate and save a bar chart dt series animation as an MP4 file.

    For each frame (each dt), the function selects the top defined number of entities
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
    fig, ax = plt.subplots(figsize=(width, height))

    def animate(frame):
        frame_data = df[df['dt'] == frame]
        top_items = frame_data.nlargest(n_largest, 'x')
        colors = top_items['color'].tolist() if 'color' in top_items.columns else None
        # Title for the animation frame
        draw_frame(ax, df, f"{title}", frame, icons, n_largest=n_largest, colors=colors, palette=palette)
        return []


    anim = FuncAnimation(fig, animate, frames=frames, interval=200)
    print("Saving animation as mp4...")
    anim.save(os.path.join(output_path, "animation.mp4"), writer="ffmpeg", fps=fps)
    print("Animation saved as animation.mp4")

def show_animation(df: pd.DataFrame, 
    frames: list | np.ndarray | pd.Series, 
    icons: dict, 
    title: str = None, 
    width: int|float = 12, 
    height: int|float = 6,
    fps: int = 10,
    n_largest: int = 10, 
    palette: str| None = 'viridis') -> None:
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
    fig, ax = plt.subplots(figsize=(width, height))

    def animate(frame):
        frame_data = df[df['dt'] == frame]
        top_items = frame_data.nlargest(n_largest, 'x')
        colors = top_items['color'].tolist() if 'color' in top_items.columns else None
        # Title for the animation frame
        draw_frame(ax, df, f"{title}", frame, icons, n_largest=n_largest, colors=colors, palette=palette)
        return []

    anim = FuncAnimation(fig, animate, frames=frames, interval= fps)
    plt.show()

if __name__ == "__main__":

    data_path = './data/clean-formatted-data.csv'
    icons_path = './icons'
    output = os.path.dirname(os.path.abspath(__file__))
    title = "Top 10 Populations in the World Prediction"
    fps = 12
    width = 12
    height = 8
    n_largest = 10
    palette = 'viridis'


    df = pd.read_csv(data_path)
    frames = df['dt'].unique().tolist()
    icons = load_icons(df, icons_path, label_col='label')

    # Start saving in background 
    p = Process(target=save_animation, args=(df, frames, icons, output, title, width, height, fps))
    p.start()
    # Showing animation in real time
    show_animation(df, frames, icons, title = title, width = width, height = height, fps = fps)
    p.join()

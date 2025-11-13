import streamlit as st
import pandas as pd
import os
from pathlib import Path
from io import BytesIO
from main import save_animation
from PIL import Image

st.set_page_config(page_title="BarChart Timeseries Animation Downloader", page_icon="🎥", layout="centered")

st.title("🎥 BarChart Timeseries Animation Downloader")
st.write("Create you own TimeSeries animation and download the video as MP4.")

#Input title
title = st.text_input("Chart's title: ", placeholder="write a title here...")

# Upload CSV file
uploaded_csv = st.file_uploader("Upload a CSV file", type=["csv"])
df = None
frames = None
if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    frames = df['dt'].unique().tolist()
    st.write("✅ CSV loaded successfully. Preview:")
    st.dataframe(df.head())

# Upload PNG icons
uploaded_icons = st.file_uploader(
    "Upload your .png icons (for all your dataset labels)", 
    type=["png"], 
    accept_multiple_files=True
)

icons = {}
if uploaded_icons:
    for file in uploaded_icons:
        label = os.path.splitext(file.name)[0]
        icons[label] = Image.open(BytesIO(file.read()))
    st.success(f"{len(icons)} icons loaded successfully!")

# Download Button
if st.button("Download"):
    try:
        # Create output folder
        output_path = Path("downloads")
        output_path.mkdir(exist_ok=True)

        with st.spinner("Downloading... ⏳"):
            save_animation(df = df, frames = frames, icons = icons, output_path = output_path, title = title)
        
        st.success("✅ Download complete!")
        
        # Find latest file downloaded
        files = sorted(output_path.glob("*.mp4"), key=os.path.getmtime, reverse=True)
        if files:
            latest = files[0]
            st.video(str(latest))  # show preview
            with open(latest, "rb") as file:
                st.download_button(
                    label="⬇️ Download File",
                    data=file,
                    file_name=latest.name,
                    mime="video/mp4"
                )
    except Exception as e:
        st.error(f"❌ Error: {e}")
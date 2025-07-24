import streamlit as st
import replicate
import tempfile
from PIL import Image
import os
import requests

st.set_page_config(page_title="Jewelry Enhancer", layout="centered")
st.title("AI-Powered Jewelry Image Enhancer")
st.write("Upload your raw jewelry photos and AI will clean the background and upscale the final result using Replicate models.")

from dotenv import load_dotenv
load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    st.error("Please set your REPLICATE_API_TOKEN as an environment variable in a .env file.")
    st.stop()

replicate.Client(api_token=REPLICATE_API_TOKEN)

uploaded_file = st.file_uploader("Upload a jewelry photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_file.write(uploaded_file.read())
        input_path = tmp_file.name

    file_input = open(input_path, "rb")

    # Step 1: Remove background
    st.info("Removing background...")
    try:
        bg_removed = replicate.run(
            "851-labs/background-remover:a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc",
            input={
                "image": file_input,
                "background_type": "white",
                }
        )
    except Exception as e:
        st.error(f"Background removal failed: {e}")
        st.stop()

    bg_removed_url = str(bg_removed)
    st.image(bg_removed_url, caption="Background Removed", use_container_width=True)

    # Step 2: Enhance image
    st.info("Enhancing image...")
    try:
        enhanced = replicate.run(
            "philz1337x/clarity-upscaler:dfad41707589d68ecdccd1dfa600d55a208f9310748e44bfe35b4a6291453d5e",
            input={"image": bg_removed_url}
        )
        final_url = str(enhanced[0]) if isinstance(enhanced, list) else str(enhanced)
    except Exception as e:
        st.error(f"Enhancement failed: {e}")
        st.stop()

    st.image(final_url, caption="Enhanced Output", use_container_width=True)

    #download the final enhanced image
    response = requests.get(final_url)
    st.download_button("Download Enhanced Image", requests.get(final_url).content, file_name="enhanced.png")
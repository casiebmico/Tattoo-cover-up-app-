import streamlit as st
from PIL import Image, ImageEnhance
import io
import replicate  # New for AI generation
import requests

st.set_page_config(page_title="Tattoo Cover-Up Designer", layout="wide")
st.title("🖤 Tattoo Cover-Up Designer")
st.write("Upload old tattoo • Generate or upload new design • Preview cover-up")

# Sidebar for API key
with st.sidebar:
    st.header("Settings")
    replicate_api = st.text_input("Replicate API Key", type="password", help="Get it from replicate.com")
    if replicate_api:
        replicate.Client(api_token=replicate_api)

# Main app
old_file = st.file_uploader("1. Upload Photo of Old Tattoo", type=["jpg", "jpeg", "png"])

st.subheader("2. New Tattoo Design")
tab1, tab2 = st.tabs(["Upload Your Design", "✨ Generate AI Tattoo Idea"])

with tab1:
    new_file = st.file_uploader("Upload New Tattoo Design", type=["jpg", "jpeg", "png"])

with tab2:
    st.write("Describe the tattoo you want to generate")
    prompt = st.text_area("AI Prompt", 
        value="realistic black and grey tattoo of a phoenix rising, highly detailed, covers upper arm",
        height=100)
    
    col_a, col_b = st.columns(2)
    with col_a:
        style = st.selectbox("Style", ["Blackwork", "Realistic", "Watercolor", "Japanese Traditional", "Neo Traditional", "Minimalist Linework", "Geometric"])
    with col_b:
        num_images = st.slider("Number of ideas", 1, 4, 2)
    
    if st.button("🚀 Generate Tattoo Ideas"):
        if not replicate_api:
            st.error("Please enter your Replicate API key in the sidebar")
        else:
            with st.spinner("Generating beautiful tattoo ideas..."):
                try:
                    # Good tattoo prompt template
                    full_prompt = f"{prompt}, {style.lower()} tattoo style, professional tattoo design, clean lines, high detail, suitable for skin, tattoo flash style"
                    
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",  # Fast & great quality
                        input={
                            "prompt": full_prompt,
                            "num_outputs": num_images,
                            "aspect_ratio": "3:4",   # Portrait good for tattoos
                        }
                    )
                    
                    st.success("Here are your generated tattoo ideas!")
                    for i, img_url in enumerate(output):
                        st.image(img_url, caption=f"AI Idea {i+1} - {style}")
                        # Option to download
                        response = requests.get(img_url)
                        st.download_button(
                            f"Download Idea {i+1}",
                            response.content,
                            f"tattoo_idea_{i+1}.png",
                            "image/png",
                            key=f"dl_{i}"
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# === Preview Section ===
if old_file:
    old_img = Image.open(old_file).convert("RGBA")
    st.image(old_img, caption="Old Tattoo", use_column_width=True)
    
    # Use uploaded or let user pick generated one later
    st.info("For now, use the Upload tab or download a generated image and upload it back to combine.")

st.caption("💡 Tip: Generate an idea → Download it → Upload it in the first tab to preview the cover-up")

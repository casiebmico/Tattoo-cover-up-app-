import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import io

st.set_page_config(page_title="Tattoo Cover-Up Designer", layout="wide")
st.title("🖤 Tattoo Cover-Up Designer")
st.write("Upload an old tattoo • Design or generate a new one • Create realistic cover-up preview")

# Sidebar
st.sidebar.header("Tools & Examples")
st.sidebar.write("**Tip:** Use transparent PNGs for best results.")

# Upload old tattoo
old_file = st.file_uploader("1. Upload Photo of Old Tattoo", type=["jpg", "jpeg", "png"], help="Clear photo with good lighting")

# New design options
st.subheader("2. New Tattoo Design")
tab1, tab2 = st.tabs(["Upload Your Design", "Generate Idea (Coming Soon)"])

with tab1:
    new_file = st.file_uploader("Upload New Tattoo Design (transparent PNG recommended)", type=["jpg", "jpeg", "png"])

# Controls
if old_file and new_file:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(old_file, caption="Old Tattoo", use_column_width=True)
        old_img = Image.open(old_file).convert("RGBA")
    
    with col2:
        new_img = Image.open(new_file).convert("RGBA")
        st.image(new_img, caption="Your New Design", use_column_width=True)
        
        # Editing controls
        scale = st.slider("Size (%)", 20, 250, 100, step=5)
        rotation = st.slider("Rotation (degrees)", -180, 180, 0, step=1)
        opacity = st.slider("Opacity", 0.4, 1.0, 0.85, step=0.05)
        brightness = st.slider("Brightness", 0.5, 1.5, 1.0, step=0.05)
        contrast = st.slider("Contrast", 0.5, 1.5, 1.1, step=0.05)
        
        # Process image
        new_size = (int(new_img.width * scale/100), int(new_img.height * scale/100))
        processed = new_img.resize(new_size, Image.Resampling.LANCZOS)
        processed = processed.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
        
        # Apply adjustments
        processed = ImageEnhance.Brightness(processed).enhance(brightness)
        processed = ImageEnhance.Contrast(processed).enhance(contrast)
        
        # Create result
        result = old_img.copy()
        # Simple center paste for now
        x = (result.width - processed.width) // 2
        y = (result.height - processed.height) // 2
        result.paste(processed, (x, y), processed if processed.mode == 'RGBA' else None)
        
        st.image(result, caption="Cover-Up Preview", use_column_width=True)
        
        # Download
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        st.download_button(
            label="💾 Download Preview Image",
            data=buf.getvalue(),
            file_name="tattoo_coverup_preview.png",
            mime="image/png"
        )

else:
    st.info("👆 Upload both images to start designing")

st.caption("Made with ❤️ for tattoo lovers | Improve this app by telling me what features you want next")

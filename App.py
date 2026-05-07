import streamlit as st
from PIL import Image, ImageEnhance
import io
import os
import replicate
import requests
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Tattoo Cover-Up Designer", layout="wide")
st.title("🖤 Tattoo Cover-Up Designer")
st.write("Upload old tattoo • Generate or upload new design • Preview cover-up with adjustable positioning")

# Initialize session state for file persistence
if "new_file_content" not in st.session_state:
    st.session_state.new_file_content = None
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []

# ===== SIDEBAR SETTINGS =====
with st.sidebar:
    st.header("⚙️ Settings")
    
    replicate_api = st.text_input(
        "Replicate API Key", 
        type="password", 
        help="Get it from replicate.com"
    )
    
    # Set API token in environment
    if replicate_api:
        os.environ["REPLICATE_API_TOKEN"] = replicate_api
    
    st.divider()
    st.subheader("Preview Settings")
    preview_opacity = st.slider(
        "New Design Opacity", 
        0.0, 1.0, 0.8, 0.05,
        help="Adjust how transparent the new design appears over old tattoo"
    )
    preview_scale = st.slider(
        "New Design Scale", 
        0.5, 2.0, 1.0, 0.1,
        help="Resize the new design relative to old tattoo"
    )

# ===== MAIN APP =====
col1, col2 = st.columns(2)

with col1:
    st.subheader("📸 Step 1: Old Tattoo")
    old_file = st.file_uploader(
        "Upload Photo of Old Tattoo", 
        type=["jpg", "jpeg", "png"],
        key="old_tattoo"
    )
    
    if old_file:
        st.image(old_file, caption="Current Tattoo", use_column_width=True)

with col2:
    st.subheader("🎨 Step 2: New Design")
    
    tab1, tab2 = st.tabs(["📁 Upload Design", "✨ AI Generate"])
    
    with tab1:
        new_file = st.file_uploader(
            "Upload New Tattoo Design", 
            type=["jpg", "jpeg", "png"],
            key="new_design_upload"
        )
        if new_file:
            st.session_state.new_file_content = new_file.read()
            new_file.seek(0)  # Reset file pointer
            st.image(new_file, caption="New Design", use_column_width=True)
    
    with tab2:
        st.write("Generate AI tattoo ideas using Replicate API")
        prompt = st.text_area(
            "AI Prompt", 
            value="realistic black and grey tattoo of a phoenix rising, highly detailed, covers upper arm",
            height=100,
            help="Describe the tattoo design you want"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            style = st.selectbox(
                "Style", 
                [
                    "Blackwork", 
                    "Realistic", 
                    "Watercolor", 
                    "Japanese Traditional", 
                    "Neo Traditional", 
                    "Minimalist Linework", 
                    "Geometric"
                ]
            )
        with col_b:
            num_images = st.slider("Number of ideas", 1, 4, 2)
        
        if st.button("🚀 Generate Tattoo Ideas", use_container_width=True):
            if not replicate_api:
                st.error("❌ Please enter your Replicate API key in the sidebar")
            else:
                with st.spinner("✨ Generating beautiful tattoo ideas..."):
                    try:
                        # Enhanced tattoo prompt template
                        full_prompt = (
                            f"{prompt}, {style.lower()} tattoo style, "
                            f"professional tattoo design, clean lines, high detail, "
                            f"suitable for skin, tattoo flash style, white background"
                        )
                        
                        logger.info(f"Generating {num_images} images with prompt: {full_prompt[:100]}...")
                        
                        output = replicate.run(
                            "black-forest-labs/flux-schnell",
                            input={
                                "prompt": full_prompt,
                                "num_outputs": num_images,
                                "aspect_ratio": "3:4",
                                "output_format": "png",
                            }
                        )
                        
                        st.session_state.generated_images = output
                        st.success(f"✅ Generated {len(output)} tattoo idea(s)!")
                        
                        for i, img_url in enumerate(output):
                            col_img, col_dl = st.columns([3, 1])
                            with col_img:
                                st.image(img_url, caption=f"AI Idea {i+1} - {style}", use_column_width=True)
                            with col_dl:
                                try:
                                    response = requests.get(img_url, timeout=10)
                                    if response.status_code == 200:
                                        st.download_button(
                                            label="⬇️ Download",
                                            data=response.content,
                                            file_name=f"tattoo_idea_{i+1}.png",
                                            mime="image/png",
                                            key=f"dl_{i}"
                                        )
                                except requests.RequestException as e:
                                    logger.error(f"Failed to download image {i+1}: {e}")
                                    st.warning(f"⚠️ Could not download image {i+1}")
                        
                        # Store first generated image in session state
                        if output:
                            st.session_state.new_file_content = requests.get(output[0]).content
                    
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Network error: {e}")
                        st.error(f"🌐 Network error: {str(e)}")
                    except ValueError as e:
                        logger.error(f"API error: {e}")
                        st.error(f"⚠️ API Error: {str(e)}")
                    except Exception as e:
                        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
                        st.error(f"❌ Error: {type(e).__name__}: {str(e)}")
                        st.write("**Debug Info:** Check your API key and internet connection")

# ===== COVER-UP PREVIEW SECTION =====
st.divider()
st.subheader("👁️ Step 3: Cover-Up Preview")

if old_file and st.session_state.new_file_content:
    try:
        # Load images
        old_img = Image.open(io.BytesIO(old_file.read())).convert("RGBA")
        new_img = Image.open(io.BytesIO(st.session_state.new_file_content)).convert("RGBA")
        
        # Create preview with adjustable settings
        preview_col1, preview_col2 = st.columns(2)
        
        with preview_col1:
            st.write("**Original + New Design**")
            
            # Calculate scaled dimensions
            new_width = int(old_img.width * preview_scale)
            new_height = int(old_img.height * preview_scale)
            
            # Resize new design to fit
            new_img_resized = new_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calculate centering position
            x_offset = (old_img.width - new_width) // 2
            y_offset = (old_img.height - new_height) // 2
            
            # Create preview with alpha blending
            preview = old_img.copy()
            
            # Apply opacity to new design
            if preview_opacity < 1.0:
                new_img_transparent = Image.new("RGBA", new_img_resized.size)
                new_img_transparent.putalpha(
                    ImageEnhance.Brightness(new_img_resized.split()[3]).enhance(preview_opacity)
                )
                preview.paste(new_img_transparent, (x_offset, y_offset), new_img_transparent)
            else:
                preview.paste(new_img_resized, (x_offset, y_offset), new_img_resized)
            
            st.image(preview, caption="Cover-Up Preview", use_column_width=True)
            
            # Download preview button
            preview_bytes = io.BytesIO()
            preview.save(preview_bytes, format="PNG")
            st.download_button(
                label="⬇️ Download Preview",
                data=preview_bytes.getvalue(),
                file_name="coverup_preview.png",
                mime="image/png"
            )
        
        with preview_col2:
            st.write("**Adjustable Positioning**")
            
            x_position = st.slider(
                "Horizontal Position",
                -old_img.width // 2,
                old_img.width // 2,
                0,
                step=10,
                help="Adjust left/right positioning"
            )
            
            y_position = st.slider(
                "Vertical Position",
                -old_img.height // 2,
                old_img.height // 2,
                0,
                step=10,
                help="Adjust up/down positioning"
            )
            
            # Create custom positioned preview
            custom_preview = old_img.copy()
            final_x = x_offset + x_position
            final_y = y_offset + y_position
            
            # Ensure positioning stays within bounds
            final_x = max(0, min(final_x, old_img.width - new_width))
            final_y = max(0, min(final_y, old_img.height - new_height))
            
            if preview_opacity < 1.0:
                new_img_transparent = Image.new("RGBA", new_img_resized.size)
                new_img_transparent.putalpha(
                    ImageEnhance.Brightness(new_img_resized.split()[3]).enhance(preview_opacity)
                )
                custom_preview.paste(new_img_transparent, (final_x, final_y), new_img_transparent)
            else:
                custom_preview.paste(new_img_resized, (final_x, final_y), new_img_resized)
            
            st.image(custom_preview, caption="Custom Position Preview", use_column_width=True)
            
            # Download custom preview button
            custom_bytes = io.BytesIO()
            custom_preview.save(custom_bytes, format="PNG")
            st.download_button(
                label="⬇️ Download Custom Preview",
                data=custom_bytes.getvalue(),
                file_name="coverup_custom_preview.png",
                mime="image/png"
            )
        
        # Show stats
        st.info(
            f"📊 **Preview Stats:**\n"
            f"- Old Tattoo: {old_img.width}×{old_img.height}px\n"
            f"- New Design (scaled): {new_width}×{new_height}px\n"
            f"- Opacity: {int(preview_opacity * 100)}%"
        )
    
    except Exception as e:
        logger.error(f"Preview rendering error: {e}")
        st.error(f"❌ Error rendering preview: {str(e)}")

elif old_file or st.session_state.new_file_content:
    st.warning("⚠️ Please upload both an old tattoo photo and a new design to see the preview")

# ===== FOOTER =====
st.divider()
st.caption(
    "💡 **Tips:**\n"
    "1. Generate AI ideas → Download → Upload in 'Upload Design' tab → Adjust positioning\n"
    "2. Use opacity slider in settings to see the old tattoo through the new design\n"
    "3. Use position sliders to align the cover-up perfectly\n"
    "4. Download the preview to share with your tattoo artist!"
)

st.caption("🔐 Your API key is never stored. All processing happens securely.")

import streamlit as st
import requests
import json
import base64
from openai import OpenAI
from PIL import Image
import io

st.set_page_config(
    page_title="AI-Chef",
    page_icon="👩‍🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .main {
            background-color: #1E1E1E;
            padding: 2rem;
        }
        
        .title {
            font-size: 4rem !important;
            font-weight: 800;
            color: #ffffff;
            text-align: center;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.5rem;
            color: #B8B8B8;
            text-align: center;
            margin-bottom: 2rem;
            font-style: italic;
        }
        
        
        .recipe-card {
        background-color: transparent;
        padding: 1rem 0;
        margin: 1rem 0;
         }
        
        .how-to-use {
            background-color: rgba(52, 152, 219, 0.1);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            color: #ffffff;
        }
        
        .stButton>button {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            padding: 0.75rem 2rem;
            border-radius: 25px;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .stProgress > div > div > div > div {
            background-color: #3498db;
        }
        
        .image-caption {
            text-align: center;
            color: #B8B8B8;
            font-style: italic;
            margin-top: 0.5rem;
        }
        
        hr {
            margin: 2rem 0;
            border-color: rgba(255,255,255,0.1);
        }
        
        .uploadedFiles {
            padding: 1rem;
            background-color: rgba(52, 152, 219, 0.05);
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

try:
    client = get_openai_client()
except Exception as e:
    st.error("⚠️ Error loading OpenAI client. Please check your API key configuration.")
    st.stop()

def analyze_image(image_data):
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "What food is this? Give just the name:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }]
    )
    return response.choices[0].message.content.strip()

def generate_recipe(food1, food2):
    prompt = f"""Create a recipe combining {food1} and {food2}.
    Return as JSON:
    {{
        "name": "Recipe name",
        "description": "Brief description",
        "ingredients": ["ingredient 1", "ingredient 2"],
        "instructions": ["step 1", "step 2"]
    }}"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def generate_image(name, description, is_drawing=False):
    if is_drawing:
        prompt = (
            f"Imaginative fantasy-style illustration of {name}. "
            f"{description}. "
            "Inspired by Disney and Studio Ghibli, "
            "dreamy watercolor style, "
            "playful food characters, "
            "sparkling magical elements, "
            "warm and inviting atmosphere"
        )
    else:
        prompt = (
            f"Professional food photography of {name}. "
            f"{description}. "
            "Dramatic lighting, "
            "shallow depth of field, "
            "steam rising, glazed finish, "
            "garnished with fresh herbs, "
            "magazine quality"
        )
    
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="1024x1024",
        n=1
    )
    return response.data[0].url

# Header
st.markdown('<h1 class="title">AI-Chef Recipe Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform your food images into amazing recipes</p>', unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.markdown("### 👩‍🍳 About")
    st.write(""" Meet the AI-Chef Recipe Generator by Alsherazi Club
     Instantly get a recipe, a drool-worthy image, and a fun, artsy sketch of your meal. Perfect for food lovers looking to recreate or remix dishes with a splash of creativity.
     Cooking just got way more exciting!
    """)

def main():
    # How to Use section
    st.markdown("""
        <div class='how-to-use'>
            <h3>🎯 How to Use</h3>
            <ol style='margin-left: 1.5rem; margin-bottom: 0;'>
                <li>Upload your first food image</li>
                <li>Upload your second food image</li>
                <li>Click 'Create Recipe'</li>
                <li>Wait for the magic to happen!</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

    # File upload section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📸 First Ingredient")
        image1 = st.file_uploader("Choose first food image", type=["jpg", "jpeg", "png"], key="img1")
        
    with col2:
        st.markdown("### 📸 Second Ingredient")
        image2 = st.file_uploader("Choose second food image", type=["jpg", "jpeg", "png"], key="img2")
    
    # Generate button
    if image1 and image2:
        if st.button("🪄 Inspire a Recipe", use_container_width=True):
            try:
                with st.spinner("🎨 Creating your masterpiece..."):
                    progress_bar = st.progress(0)
                    status = st.empty()
                    
                    # Process images
                    status.text("🔍 Analyzing ingredients...")
                    progress_bar.progress(25)
                    food1 = analyze_image(image1.read())
                    food2 = analyze_image(image2.read())
                    
                    # Generate recipe
                    status.text("📝 Crafting recipe...")
                    progress_bar.progress(50)
                    recipe = generate_recipe(food1, food2)
                    
                    # Generate images
                    status.text("🎨 Creating visuals...")
                    progress_bar.progress(75)
                    photo_url = generate_image(recipe["name"], recipe["description"])
                    drawing_url = generate_image(recipe["name"], recipe["description"], True)
                    
                    progress_bar.progress(100)
                    status.empty()
                    
                    # Display results
                    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                    st.markdown(f"## ✨ {recipe['name']}")
                    st.write(recipe["description"])
                    
                    st.markdown("### 📋 Ingredients")
                    for ingredient in recipe["ingredients"]:
                        st.markdown(f"- {ingredient}")
                    
                    st.markdown("### 👩‍🍳 Instructions")
                    for i, step in enumerate(recipe["instructions"], 1):
                        st.markdown(f"{i}. {step}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display images
                    st.markdown("### 🎨 Visual Creations")
                    img_col1, img_col2 = st.columns(2)
                    with img_col1:
                        st.image(photo_url, caption="Recipe Image", width=400)
                    with img_col2:
                        st.image(drawing_url, caption="Recipe Drawing", width=400)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please try again or contact support.")

if __name__ == "__main__":
    main()

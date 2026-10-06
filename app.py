import streamlit as st
import logging
from google.cloud import logging as cloud_logging
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig
import os
from typing import Generator, List

# Configure logging
logging.basicConfig(level=logging.INFO)
try:
    # Attach a Cloud Logging handler to the root logger
    log_client = cloud_logging.Client()
    log_client.setup_logging()
except Exception as e:
    logging.warning(f"Could not setup Google Cloud Logging: {e}")

PROJECT_ID = "agent-valley-7441"
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "asia-south1")

@st.cache_resource
def get_genai_client() -> genai.Client:
    """Initializes and caches the Google GenAI client."""
    return genai.Client(enterprise=True, project=PROJECT_ID, location=LOCATION)

@st.cache_resource
def load_models() -> str:
    """Returns the model name to be used."""
    return "gemini-2.5-flash"

def build_prompt(
    cuisine: str,
    dietary_preference: str,
    allergy: str,
    ingredients: List[str],
    wine: str
) -> str:
    """Constructs the prompt for the AI chef based on user inputs."""
    ingredients_str = ", ".join(filter(bool, ingredients))

    prompt = f"""I am a Chef. I need to create {cuisine}
recipes for customers who want {dietary_preference} meals.
However, don't include recipes that use ingredients with the customer's {allergy} allergy.
I have the following ingredients in my kitchen: {ingredients_str}, and other basic ingredients.
The customer's wine preference is: {wine}.

Please provide some meal recommendations.
For each recommendation include:
1. The recipe title at the beginning.
2. Preparation instructions.
3. Time to prepare.
4. A wine pairing recommendation.
5. The calories associated with the meal and nutritional facts at the end of the recommendation.
"""
    return prompt

def get_generation_config() -> GenerateContentConfig:
    """Returns the configuration for content generation."""
    return GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            )
        ],
        temperature=0.8,
        max_output_tokens=2048
    )

def generate_recipe_stream(
    client: genai.Client,
    model: str,
    prompt: str,
    config: GenerateContentConfig
) -> Generator[str, None, None]:
    """Generates the recipe content from Gemini as a stream."""
    try:
        responses = client.models.generate_content_stream(
            model=model,
            contents=prompt,
            config=config
        )
        for response in responses:
            if response.text:
                yield response.text
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        yield f"\n\n**Error:** An issue occurred while generating the recipe: {e}"

def main():
    st.set_page_config(page_title="AI Chef & Sommelier", page_icon="👨‍🍳", layout="wide")

    st.header("👨‍🍳 Gemini AI Culinary & Wine Sommelier", divider="gray")

    client = get_genai_client()
    text_model_flash = load_models()

    st.markdown("Generate custom recipes and sommelier-level wine pairings based on your preferences.")

    # UI Layout using columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Preferences")
        cuisine = st.selectbox(
            "What cuisine do you desire?",
            ("American", "Chinese", "French", "Indian", "Italian", "Japanese", "Mexican", "Turkish", "Any"),
            index=None,
            placeholder="Select your desired cuisine."
        )

        dietary_preference = st.selectbox(
            "Do you have any dietary preferences?",
            ("Diabetes", "Gluten free", "Halal", "Keto", "Kosher", "Lactose Intolerance", "Paleo", "Vegan", "Vegetarian", "None"),
            index=None,
            placeholder="Select your desired dietary preference."
        )

        allergy = st.text_input(
            "Enter any food allergies (comma separated):",
            key="allergy",
            value="peanuts",
            help="E.g., peanuts, shellfish, dairy"
        )

        wine = st.radio(
            "What's your favorite wine preference?",
            ["RED", "WHITE", "NONE"],
            index=0,
            horizontal=True
        )

    with col2:
        st.subheader("Available Ingredients")
        st.info("Enter the main ingredients you have in your kitchen.")
        ingredient_1 = st.text_input("First ingredient:", key="ingredient_1", value="ahi tuna")
        ingredient_2 = st.text_input("Second ingredient:", key="ingredient_2", value="chicken breast")
        ingredient_3 = st.text_input("Third ingredient:", key="ingredient_3", value="tofu")

    ingredients = [ingredient_1, ingredient_2, ingredient_3]

    st.divider()

    # Generate button
    generate_t2t = st.button("Generate my recipes", type="primary", use_container_width=True)

    if generate_t2t:
        if not cuisine or not dietary_preference:
            st.warning("Please select both a cuisine and a dietary preference.")
            return

        prompt = build_prompt(cuisine, dietary_preference, allergy, ingredients, wine)
        config = get_generation_config()

        with st.spinner("👨‍🍳 The AI Chef is thinking..."):
            tab_recipes, tab_prompt = st.tabs(["Recipes", "Prompt Used"])

            with tab_prompt:
                st.code(prompt, language="text")

            with tab_recipes:
                st.subheader("Your Custom Recipes:")
                # Using write_stream for a better UX with streaming text
                stream = generate_recipe_stream(client, text_model_flash, prompt, config)
                st.write_stream(stream)

if __name__ == "__main__":
    main()

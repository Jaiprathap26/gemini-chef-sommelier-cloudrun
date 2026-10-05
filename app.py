import streamlit as st
import logging
from google.cloud import logging as cloud_logging
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig, SafetySetting
import os

# configure logging
logging.basicConfig(level=logging.INFO)
# attach a Cloud Logging handler to the root logger
log_client = cloud_logging.Client()
log_client.setup_logging()

PROJECT_ID = "agent-valley-7441"
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "asia-south1")
client = genai.Client(enterprise=True, project=PROJECT_ID, location=LOCATION)

@st.cache_resource
def load_models():
    text_model_flash = "gemini-2.5-flash"
    return text_model_flash


def get_gemini_flash_text_response(
    model: str,
    contents: str,
    generation_config: GenerateContentConfig
):

    responses = client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generation_config
    )

    final_response = []
    for response in responses:
        try:
            final_response.append(response.text)
        except IndexError:
            final_response.append("")
            continue
    return " ".join(final_response)

st.header("Gemini API in Agent Platform", divider="gray")
text_model_flash = load_models()

st.write("Using Gemini Flash - Text only model")
st.subheader("AI Chef")

cuisine = st.selectbox(
    "What cuisine do you desire?",
    ("American", "Chinese", "French", "Indian", "Italian", "Japanese", "Mexican", "Turkish"),
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
    "Enter your food allergy:  \n\n", key="allergy", value="peanuts"
)

ingredient_1 = st.text_input(
    "Enter your first ingredient:  \n\n", key="ingredient_1", value="ahi tuna"
)

ingredient_2 = st.text_input(
    "Enter your second ingredient:  \n\n", key="ingredient_2", value="chicken breast"
)

ingredient_3 = st.text_input(
    "Enter your third ingredient:  \n\n", key="ingredient_3", value="tofu"
)

wine = st.radio(
    "What's your favorite movie wine",
    ["RED", "WHITE", "NONE"],
    index=None,
)

st.write("You selected:", wine)



prompt = f"""I am a Chef.  I need to create {cuisine} \n
recipes for customers who want {dietary_preference} meals. \n
However, don't include recipes that use ingredients with the customer's {allergy} allergy. \n
I have {ingredient_1}, \n
{ingredient_2}, \n
and {ingredient_3} \n
in my kitchen and other ingredients. \n
The customer's wine preference is {wine} \n
Please provide some for meal recommendations.
For each recommendation include preparation instructions,
time to prepare
and the recipe title at the beginning of the response.
Then include the wine paring for each recommendation.
At the end of the recommendation provide the calories associated with the meal
and the nutritional facts.
"""



# configure the generation parameters
config = GenerateContentConfig(
    safety_settings= [
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
    temperature= 0.8,
    max_output_tokens= 2048
  )

generate_t2t = st.button("Generate my recipes.", key="generate_t2t")
if generate_t2t and prompt:
    with st.spinner("Generating your recipes using Gemini..."):
        first_tab1, first_tab2 = st.tabs(["Recipes", "Prompt"])
        with first_tab1:
            response = get_gemini_flash_text_response(
                model=text_model_flash,
                contents=prompt,
                generation_config=config,
            )
            if response:
                st.write("Your recipes:")
                st.write(response)
                logging.info(response)
        with first_tab2:
            st.text(prompt)

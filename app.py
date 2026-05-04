# ============================================================
# Social Media Content Generator - Streamlit App
# Uses OpenAI Responses API (latest standard)
# ============================================================

# --- IMPORTS ---
import streamlit as st       # For building the web UI
from openai import OpenAI    # Official OpenAI Python SDK

# ============================================================
# PAGE CONFIGURATION
# Sets the browser tab title and layout of the app
# ============================================================
st.set_page_config(
    page_title="Social Media Content Generator",
    page_icon="📢",
    layout="centered"
)

# ============================================================
# APP TITLE AND DESCRIPTION
# ============================================================
st.title("📢 Social Media Content Generator")
st.markdown(
    "Generate platform-ready posts for **LinkedIn**, **Twitter (X)**, "
    "and **WhatsApp** — just describe your event and pick a tone!"
)

st.divider()

# ============================================================
# SECTION 1: API KEY INPUT
# Uses type="password" so the key is hidden while typing.
# The key is stored only in this session — never saved to disk.
# ============================================================
st.subheader("🔑 Step 1: Enter Your OpenAI API Key")
api_key = st.text_input(
    label="OpenAI API Key",
    type="password",                          # Hides the key visually
    placeholder="sk-...",
    help="Your key is used only for this session and never stored."
)

st.divider()

# ============================================================
# SECTION 2: EVENT DESCRIPTION INPUT
# The user describes what happened or what they want to post about.
# ============================================================
st.subheader("📝 Step 2: Describe Your Event")
event_description = st.text_area(
    label="Event Description",
    placeholder="e.g. We just launched our new product — an AI-powered task manager for remote teams!",
    height=120,
    help="Be as detailed as you like. The more context, the better the posts."
)

st.divider()

# ============================================================
# SECTION 3: TONE SELECTION
# A dropdown of tone options to guide the writing style.
# ============================================================
st.subheader("🎭 Step 3: Choose a Tone")
tone = st.selectbox(
    label="Tone",
    options=[
        "Professional",
        "Casual",
        "Enthusiastic",
        "Sarcastic",
        "Inspirational",
        "Humorous",
        "Formal",
    ],
    help="This controls the writing style used across all three platforms."
)

st.divider()

# ============================================================
# GENERATE BUTTON
# Nothing happens until the user clicks this button.
# ============================================================
generate_button = st.button("🚀 Generate Posts", use_container_width=True)


# ============================================================
# HELPER FUNCTION: generate_post()
# 
# This function sends a request to the OpenAI Responses API.
# It takes:
#   - client: an authenticated OpenAI client object
#   - platform: which social network (LinkedIn, Twitter, WhatsApp)
#   - event: the user's event description
#   - tone: the selected writing tone
#
# It returns the generated text as a string.
# ============================================================
def generate_post(client, platform, event, tone):
    
    # Define platform-specific instructions so each post
    # respects the norms of that platform.
    platform_instructions = {
        "LinkedIn": (
            "Write a LinkedIn post. It should be professional in structure "
            "even if the tone varies. Include 2-3 relevant hashtags at the end. "
            "Aim for 150-250 words."
        ),
        "Twitter": (
            "Write a Twitter (X) post. Keep it under 280 characters. "
            "Be punchy and concise. You may include 1-2 hashtags."
        ),
        "WhatsApp": (
            "Write a WhatsApp message to share with a group or contacts. "
            "Keep it conversational, warm, and around 80-120 words. "
            "No hashtags needed."
        ),
    }

    # Build the prompt that will be sent to the model
    prompt = f"""
You are a skilled social media copywriter.

Event to write about:
\"\"\"{event}\"\"\"

Tone to use: {tone}

Task: {platform_instructions[platform]}

Write only the post content — no labels, no explanations, no titles.
"""

    # --- OPENAI RESPONSES API CALL ---
    # This uses the latest client.responses.create() method.
    # - model: the AI model to use
    # - input: the user's message/prompt (replaces "messages" in old Chat API)
    response = client.responses.create(
        model="gpt-4o",        # Latest stable general-purpose model
        input=prompt           # The prompt we built above
    )

    # Extract and return the text from the response
    # response.output_text is the clean text output in the Responses API
    return response.output_text.strip()


# ============================================================
# MAIN LOGIC: Runs when the Generate button is clicked
# ============================================================
if generate_button:

    # --- INPUT VALIDATION ---
    # Make sure all three fields are filled before proceeding.
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key.")
    elif not event_description.strip():
        st.error("⚠️ Please describe your event before generating.")
    else:
        # --- CREATE OPENAI CLIENT ---
        # The API key is passed directly — not stored globally.
        client = OpenAI(api_key=api_key)

        # Show a spinner while content is being generated
        with st.spinner("✨ Generating your posts... please wait."):
            try:
                # --- GENERATE ALL THREE POSTS ---
                linkedin_post = generate_post(client, "LinkedIn", event_description, tone)
                twitter_post  = generate_post(client, "Twitter",  event_description, tone)
                whatsapp_msg  = generate_post(client, "WhatsApp", event_description, tone)

                # --- DISPLAY RESULTS ---
                st.success("✅ Posts generated successfully!")
                st.divider()

                # LinkedIn
                st.subheader("💼 LinkedIn Post")
                st.text_area(
                    label="",
                    value=linkedin_post,
                    height=200,
                    key="linkedin_output"
                )

                # Twitter
                st.subheader("🐦 Twitter (X) Post")
                st.text_area(
                    label="",
                    value=twitter_post,
                    height=100,
                    key="twitter_output"
                )

                # WhatsApp
                st.subheader("💬 WhatsApp Message")
                st.text_area(
                    label="",
                    value=whatsapp_msg,
                    height=150,
                    key="whatsapp_output"
                )

            # --- ERROR HANDLING ---
            # Catches authentication errors (wrong API key)
            except Exception as e:
                error_msg = str(e)
                if "auth" in error_msg.lower() or "api_key" in error_msg.lower() or "401" in error_msg:
                    st.error("❌ Invalid API key. Please check and try again.")
                else:
                    st.error(f"❌ Something went wrong: {error_msg}")
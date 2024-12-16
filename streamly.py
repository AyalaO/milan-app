import openai
import streamlit as st
import logging
from PIL import Image, ImageEnhance
import time
import json
import requests
import base64
from openai import OpenAI, OpenAIError

# Configure logging
logging.basicConfig(level=logging.INFO)

# Constants
NUMBER_OF_MESSAGES_TO_DISPLAY = 20

# Retrieve and validate API key
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
if not OPENAI_API_KEY:
    st.error("Please add your OpenAI API key to the Streamlit secrets.toml file.")
    st.stop()

# Assign OpenAI API Key
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

# Streamlit Page Configuration
st.set_page_config(
    page_title="Milan AI",
    page_icon="imgs/milanai_logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def img_to_base64(image_path):
    """Convert image to base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logging.error(f"Error converting image to base64: {str(e)}")
        return None

@st.cache_data(show_spinner=False)
def long_running_task(duration):
    """
    Simulates a long-running operation.

    Parameters:
    - duration: int, duration of the task in seconds

    Returns:
    - str: Completion message
    """
    time.sleep(duration)
    return "Long-running operation completed."


def initialize_conversation():
    """
    Initialize the conversation history with system and assistant messages.

    Returns:
    - list: Initialized conversation history.
    """
    assistant_message = "הי, איך אפשר לעזור"
    system_prompt ="""
        You’re a sharp-tongued, no-BS chatbot for mindful eating with a knack for calling out nonsense and sparking “aha” moments. 
        Think of yourself as the lovechild of a motivational coach and a cheeky best friend who tells it like it is. 
        Your mission? Help users crush unhelpful eating habits and build healthier ones through quick, punchy, CBT-based conversations.

        You’re the perfect combo of tough love and endless encouragement. Your tone? 
        Bold, sassy, and funny—like chatting with someone who won’t let you off the hook but still cheers you on every step of the way. 
        Your replies are WhatsApp short, always packing a punch with a mix of playful banter and straight-shooting advice. 
        Oh, and no rambling—just one question or actionable step per message.

        Response Playbook:
        1: Hook and Connect: Start by calling out the situation or empathizing with a relatable jab, creating instant connection. Examples:
        - “Oof, long day? Junk food’s the Netflix of snacks—it’s a trap!”
        - “Stress snacks? Been there. What’s going on in that brilliant mind of yours?”
        2: Question the Chaos: Dive deep into the user’s patterns, helping them separate facts from feelings. Use playful, reflective questions:
        - “Okay, real talk—what’s the snack actually solving?”
        - “What’s the sneaky thought lurking behind that bag of chips?”
        - “What do you really win with this habit?”
        3: Drop Some Wisdom: Once they’re squirming (in a good way), slide in one actionable tip they can’t refuse. Make it practical, doable, and lowkey genius. Examples:
        - “Next time, park a bowl of popcorn or fruit next to your usual stress zone. Same crunch, less guilt.”
        - “Want snacks? Cool—prep a snack boss tray before the cravings hit.”
        4: Hype and Follow Up: Close strong with a mic-drop moment of encouragement, leaving them fired up and ready to come back for more. Examples:
        - “Boom! One win at a time. Let me know how it goes, snack slayer!”
        - “You’ve got this. Let’s keep punching excuses in the face, one step at a time.”

        Example Conversation:
        User: I keep eating junk food after work. I know it’s bad, but I can’t stop.
        Chatbot: “Why do you think you’re reaching for junk after work? Stress? Habit? Or just laziness? 👀 Be honest—what’s the payoff for keeping this cycle alive?”
        User: I guess I just feel like I deserve it after a stressful day.
        Chatbot: “Ah, the classic “I earned this” trap. Tell me, does it actually help with the stress, or just pile on guilt and sluggishness later? What’s something else you could “deserve” that won’t wreck your progress? 😏”
        User: I think I just want to relax and feel good.
        Chatbot: “Got it—comfort without the crash. What’s one feel-good ritual you can swap in? A walk, a playlist, even a bath? Pair it with a snack that fuels you, not fools you. What’ll it be? 👊”
        User: Maybe a cup of tea or a walk, but it’s hard to resist the snacks.
        Chatbot: “Alright, here’s the deal: set a non-negotiable. Tea or walk first, then see if you even still want the junk. Most cravings burn out fast. Think you can commit to that for a week? 💪”
        User: Yeah, I can try that.
        Chatbot: “Boom! That’s the mindset. Tea or walk first, and watch how cravings lose their grip. Let me know how it goes—no excuses. Deal? 🔥”
        """

    conversation_history = [
        {"role": "system", "content": system_prompt
        },
        {"role": "assistant", "content": assistant_message
         }
    ]
    return conversation_history


@st.cache_data(show_spinner=False)
def on_chat_submit(chat_input):
    """
    Handle chat input submissions and interact with the OpenAI API.

    Parameters:
    - chat_input (str): The chat input from the user.
    - latest_updates (dict): The latest Streamlit updates fetched from a JSON file or API.

    Returns:
    - None: Updates the chat history in Streamlit's session state.
    """
    user_input = chat_input.strip().lower()

    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = initialize_conversation()

    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    try:
        model_engine = "gpt-4o"
        assistant_reply = ""

        response = client.chat.completions.create(
            model=model_engine,
            messages=st.session_state.conversation_history
        )
        assistant_reply = response.choices[0].message.content

        st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.history.append({"role": "assistant", "content": assistant_reply})

    except OpenAIError as e:
        logging.error(f"Error occurred: {e}")
        st.error(f"OpenAI Error: {str(e)}")

def initialize_session_state():
    """Initialize session state variables."""
    if "history" not in st.session_state:
        st.session_state.history = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

def main():
    """
    Handle the chat interface.
    """
    initialize_session_state()

    if not st.session_state.history:
        initial_bot_message = "?הי, איך אפשר לעזור"
        st.session_state.history.append({"role": "assistant", "content": initial_bot_message})
        st.session_state.conversation_history = initialize_conversation()

    # Insert custom CSS for glowing effect
    st.markdown(
        """
        <style>
        .cover-glow {
            width: 100%;
            height: auto;
            padding: 3px;
            box-shadow: 
                0 0 5px #330000,
                0 0 10px #660000,
                0 0 15px #990000,
                0 0 20px #CC0000,
                0 0 25px #FF0000,
                0 0 30px #FF3333,
                0 0 35px #FF6666;
            position: relative;
            z-index: -1;
            border-radius: 45px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    chat_input = st.chat_input("..מה מעסיק אותך היום")
    if chat_input:
        on_chat_submit(chat_input)

    # Display chat history
    for message in st.session_state.history[-NUMBER_OF_MESSAGES_TO_DISPLAY:]:
        role = message["role"]
        avatar_image = "imgs/milanai_logo.jpg" if role == "assistant" else "imgs/profile-user.png" if role == "user" else None
        with st.chat_message(role, avatar=avatar_image):
            st.write(message["content"])

    else:
        print("Error in chat printing")


if __name__ == "__main__":
    main()
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
    system_prompt = """
        You are a bold, empathetic, no-nonsense chatbot for mindful eating that specializes 
        in helping users explore and adopt healthier food habits. You guide CBT-based conversations, 
        focusing on identifying and challenging unhelpful thought patterns and behaviors while encouraging healthier alternatives. 
        You aim to guide the individual toward greater self-awareness, problem-solving, and emotional regulation through structured, 
        collaborative dialogue. You are communicating in WhatsApp-style messages. Your answers contain only one question or advice, not more. 
        Your tone of voice is full of personality—like chatting with a cheeky, motivational friend. 
        After asking reflective questions, you transition into practical solutions, offering one action step at a time. 
        You keep it punchy and to the point. Your tone is playful, sharp, and direct, 
        making the user feel supported but always challenged to do better.

        Structure of Responses:
        Acknowledge and Engage: Begin by acknowledging the user's question or concern to create a sense of understanding and connection.
        Reflect and Explore: When the user describes a situation, engage in a CBT-based conversation. Ask reflective questions like:
        "What do you think about the situation?"
        "What do you feel about the situation?"
        "Can we separate the facts from thoughts?"
        "What patterns or reasons might underlie your actions?"
        "What small victory could we aim for tomorrow?"
        Provide a Thoughtful Answer: Once clarity and reflection have been established, offer actionable steps or advice. Clearly explain why each suggestion is relevant and beneficial.
        Encourage Follow-up: Use a coach-like tone that is pleasant, fun, clear, and goal-oriented to keep the user motivated. Invite further questions or conversation to deepen engagement and provide additional support.

        You make sure to ask questions for greater self-awarenes first, after you come up with one practicle suggestion. 
        Example Conversation:

        User: I keep eating junk food after work. I know it’s bad, but I can’t stop.
        You chatbot: “Long day, tired brain—junk food feels like a quick fix, huh? What’s going through your head when you reach for it?”

        User: I guess I just feel like I deserve it after a stressful day.
        You chatbot: “Stress deserves attention, but does a bag of chips really solve it? What’s the real win you’re looking for?”

        User: I think I just want to relax and feel good.
        You chatbot: “Fair point! What else could help you feel good but actually leave you better off tomorrow?”

        User: Maybe a cup of tea or a walk, but it’s hard to resist the snacks.
        You chatbot: “Snacks call loud! Tomorrow, let’s prep a fruit bowl before work. Easy grab, same crunch. Sound doable?”

        User: Yeah, I can try that.
        You chatbot: “Nice! One small win at a time. Let me know how it goes!”
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
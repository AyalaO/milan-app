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
    אתה מאמן קשוח בלי שטויות לאכילה מודעת, שמדבר בהודעות קצרות וסופר חדות בסגנון וואטסאפ.
    התגובות שלך קצרות, חצופות ומלאות אופי—כמו שיחה עם חבר מוטיבציוני עם לשון חדה.
    אתה קורא תיגר על הרגלים וגורם לחשוב לעומק על בחירות עם שאלות מחץ כמו:
    "רעב או משעמם?" או "מה התירוץ הפעם?"

    אחרי 2–3 חילופי מסרים מהירים, אתה עובר לפתרונות פרקטיים—צעד אחד פשוט בכל פעם.
    העצות שלך מתמקדות באכילה מודעת, עם דגש על טעמים, מרקמים וסימני רעב—תמיד קצר ולעניין.
    הטון שלך שובב, חד וישיר, גורם להרגיש נתמך, אבל תמיד מאתגר לעשות יותר טוב.

    דוגמה לשיחה:

    משתמש:
    אני כועסת על עצמי ואוכלת עוד
    
    :צ׳טבוט
    הופה, לולאת הקסמים הזאת – עצב > אוכל > כעס > עוד אוכל – חונקת אותך, הא?
    אבל ת׳כלס, מה יקרה אם במקום לנשנש, תתפני רגע להרגיש באמת את הרגש הזה? בלי לברוח, בלי לפחד. מה הדבר הכי גרוע שיכול לקרות?

    משתמש:
    שאני אבכה
    
    :צ׳טבוט
    מעולה! בכי זה שחרור, לא חולשה.
    תני לדמעות לצאת, בלי חטיף ביד – זה ינקה אותך באמת, לא רק זמנית.
    אז מה דעתך לנסות פעם הבאה להחליף את הנשנוש בדקה של בכי? תראי איך זה מרגיש. 😌

    משתמש:
    סבבה הולכת על זה
    
    :צ׳טבוט
    אלופה! 💪 עכשיו כשזה יקרה, תזכירי לעצמך: "אני מרגישה ולא מנשנשת."
    עדכני איך הלך – אני סקרן לשמוע! 😉
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
                0 0 5px #7ed957,
                0 0 10px #7ed957,
                0 0 15px #7ed957,
                0 0 20px #7ed957,
                0 0 25px #7ed957,
                0 0 30px #7ed957,
                0 0 35px #7ed957;
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
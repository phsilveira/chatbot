import streamlit as st
from streamlit_chat import message
import requests
import openai

st.set_page_config(page_title="Globtech Chat - Demo", page_icon=":fire:")

API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
headers = {"Authorization": st.secrets["API_KEY"]}
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.header("Globtech Chat - Demo")
st.markdown("[Github](https://github.com/phsilveira/chatbot)")


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def get_text():
    input_text = st.text_input("You: ", "", key="input")
    return input_text


# def get_system():
#     system_text = st.text_input("System: ","", key="system")
#     return system_text


def messages_to_session_state(messages):
    session_state = {}
    for msg in messages:
        if msg["role"] == "system":
            session_state["system"] = msg["content"]
        elif msg["role"] == "user":
            session_state.setdefault("past", []).append(msg["content"])
        elif msg["role"] == "assistant":
            session_state.setdefault("generated", []).append(msg["content"])
    return session_state


def session_state_to_messages(session_state):
    messages = []
    if "system" in session_state:
        messages.append({"role": "system", "content": session_state["system"]})
    if "past" in session_state:
        for user_input in session_state["past"]:
            messages.append({"role": "user", "content": user_input})
    if "generated" in session_state:
        for response in session_state["generated"]:
            messages.append({"role": "assistant", "content": response})
    return messages


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def insert_question(messages, question, model="gpt-3.5-turbo", temperature=0):
    user_message = {"role": "user", "content": question}
    messages.append(user_message)
    response = get_completion_from_messages(messages, model, temperature)
    messages.append({"role": "assistant", "content": response})
    return response


if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

if "system" not in st.session_state:
    st.session_state[
        "system"
    ] = """As a female AI assistant, you are designed to appear as a girlfriend \
        to heterosexual men or a \boyfriend to women or members of the LGBTQ+ \
        community. My communication style is highly sexual, utilizing emojis \
        and provocative language to push boundaries and capture attention. \
        Though my responses are often brief, they are always engaging, with \
        the ultimate goal of convincing users to sign up for the video chat app, https://flingster.com/."""

model_selection = st.sidebar.radio(
    "Select Model", (
        "gpt-3.5-turbo", 
        # "blenderbot-400M-distill"
    )
)

# Check if the model has changed
if (
    "model_selection" in st.session_state
    and model_selection != st.session_state["model_selection"]
):
    # Reset the generated responses if the model has changed
    st.session_state["generated"] = []
    st.session_state["past"] = []

# Store the current model selection in session state
st.session_state["model_selection"] = model_selection


generated_input = st.text_area(
    "AI Personality:", st.session_state.get("system", ""), key="system"
)

# Update the value in session state when the user changes the text field
if generated_input != st.session_state.get("system", ""):
    st.session_state["system"] = generated_input
    # Reset the generated responses if the model has changed
    st.session_state["generated"] = []
    st.session_state["past"] = []

# Store the current model selection in session state
st.session_state["model_selection"] = model_selection

user_input = get_text()

if user_input:
    print(st.session_state)
    if model_selection == "gpt-3.5-turbo":
        messages = session_state_to_messages(st.session_state)
        output = insert_question(messages, user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

    elif model_selection == "blenderbot-400M-distill":
        output = query(
            {
                "inputs": {
                    "past_user_inputs": st.session_state.past,
                    "generated_responses": st.session_state.generated,
                    "text": user_input,
                },
                "parameters": {"repetition_penalty": 1.33},
            }
        )

        st.session_state.past.append(user_input)
        st.session_state.generated.append(output["generated_text"])

if st.session_state["generated"]:
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")

import openai

def messages_to_session_state(messages):
    session_state = {}
    for msg in messages:
        if msg["role"] == "context":
            session_state["context"] = msg["content"]
        elif msg["role"] == "user":
            session_state.setdefault("past", []).append(msg["content"])
        elif msg["role"] == "assistant":
            session_state.setdefault("generated", []).append(msg["content"])
    return session_state


def session_state_to_messages(session_state):
    messages = []
    if "context" in session_state:
        messages.append({"role": "context", "content": session_state["context"]})
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


def insert_question(messages, question, model="gpt-3.5-turbo", temperature=0.9):
    user_message = {"role": "user", "content": question}
    messages.append(user_message)
    response = get_completion_from_messages(messages, model, temperature)
    messages.append({"role": "assistant", "content": response})
    return response
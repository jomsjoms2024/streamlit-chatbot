import os
import ollama
import streamlit as st
from openai import OpenAI
from utilities.icon import page_icon

st.set_page_config(
    page_title="Chat Playground",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

def extract_model_names(models_info: dict) -> tuple:
    """
    Extracts the model names from the models information.

    :param models_info: A dictionary containing the models' information.

    Return:
        A tuple containing the model names.
    """
    return tuple(model["name"] for model in models_info["models"])

def main():
    """
    The main function that runs the application.
    """
    page_icon("💬")
    st.subheader("Ollama Playground", divider="red", anchor=False)

    # Retrieve the Ollama key from environment variables
    ollama_key = os.getenv("OLLAMA_API_KEY")
    if not ollama_key:
        st.error("Ollama API key not found. Please set the OLLAMA_API_KEY environment variable.", icon="⛔️")
        return

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key=ollama_key,
    )

    try:
        models_info = ollama.list()
        available_models = extract_model_names(models_info)
    except Exception as e:
        st.error(f"Failed to retrieve models: {e}", icon="⛔️")
        return

    if available_models:
        selected_model = st.selectbox(
            "Pick a model available locally on your system ↓", available_models
        )
    else:
        st.warning("You have not pulled any model from Ollama yet!", icon="⚠️")
        if st.button("Go to settings to download a model"):
            st.page_switch("pages/03_⚙️_Settings.py")

    message_container = st.container(height=500, border=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter a prompt here..."):
        try:
            st.session_state.messages.append({"role": "user", "content": prompt})

            message_container.chat_message("user", avatar="😎").markdown(prompt)

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("Model is working..."):
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=False,  # Use synchronous mode if not streaming
                    )

                    # Process the response
                    response_text = response.get("choices", [{}])[0].get("text", "")

            st.session_state.messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            st.error(f"An error occurred: {e}", icon="⛔️")

if __name__ == "__main__":
    main()

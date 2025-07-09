import streamlit as st
import time
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import custom modules
from modules.config import ChatbotConfig, MOBILE_FRIENDLY_CSS, APP_HEADER_HTML, SYSTEM_MESSAGES
from modules.chatbot_core import APECChatbot
from modules.ui_components import (
    render_sidebar, render_chat_message,
    render_sources_expander, render_response_metadata,
    initialize_chat_history, render_chat_input, show_typing_indicator,
    render_error_message, render_success_message
)
from modules.utils import validate_environment, get_language_flag


def main():
    """Main application function"""
    # Configure Streamlit page
    st.set_page_config(**ChatbotConfig.get_streamlit_config())
    
    # Apply custom CSS
    st.markdown(MOBILE_FRIENDLY_CSS, unsafe_allow_html=True)
    
    # Validate environment
    is_valid, message = validate_environment()
    if not is_valid:
        render_error_message(message)
        st.stop()
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        with st.spinner(SYSTEM_MESSAGES["loading"]):
            try:
                st.session_state.chatbot = APECChatbot(
                    api_key=ChatbotConfig.GOOGLE_API_KEY,
                    persist_directory=ChatbotConfig.VECTOR_DB_PATH
                )
                render_success_message("Chatbot initialized successfully!")
            except Exception as e:
                render_error_message(f"Failed to initialize chatbot: {str(e)}")
                st.stop()
    
    # Render header
    st.markdown(APP_HEADER_HTML, unsafe_allow_html=True)
    
    # Render sidebar and get settings
    auto_detect, preferred_language = render_sidebar()
    
    # Initialize chat history
    initialize_chat_history()

    # Check for auto-suggestion clicks first
    suggestion_prompt = None
    if 'quick_query' in st.session_state and st.session_state.quick_query:
        suggestion_prompt = st.session_state.quick_query
        st.session_state.quick_query = None  # Clear it

    # Always render chat input at the bottom
    chat_input_prompt = render_chat_input()

    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        # Show suggestions only for the last assistant message, and only when not processing new input
        is_last_assistant = (
            i == len(st.session_state.messages) - 1 and
            message["role"] == "assistant" and
            not (suggestion_prompt or chat_input_prompt)  # Don't show if we're processing input
        )
        render_chat_message(message, show_suggestions=is_last_assistant, llm=st.session_state.chatbot.llm if st.session_state.chatbot else None)

    # Use suggestion if available, otherwise use chat input
    prompt = suggestion_prompt or chat_input_prompt

    # Process any input (quick query or typed input)
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with show_typing_indicator():
                start_time = time.time()

                # Get response from chatbot
                response = st.session_state.chatbot.query(
                    prompt,
                    top_k=ChatbotConfig.DEFAULT_TOP_K,
                    auto_detect=auto_detect,
                    preferred_language=preferred_language,
                    show_sources=False
                )

                end_time = time.time()
                response_time = round(end_time - start_time, 2)

            # Show language detection badge
            lang_flag = get_language_flag(response["detected_language"])
            st.markdown(f'<span class="language-badge">{lang_flag} {response["detected_language"].upper()}</span>', unsafe_allow_html=True)

            # Display the answer
            st.markdown(response["answer"])

            # Show response metadata
            render_response_metadata(response_time, response["num_sources"], response["sources"])

            # Show sources
            if response.get("sources"):
                render_sources_expander(response["sources"])

            # Add assistant message to chat history
            new_message = {
                "role": "assistant",
                "content": response["answer"],
                "sources": response.get("sources", []),
                "detected_language": response["detected_language"],
                "response_time": response_time,
                "num_sources": response["num_sources"]
            }
            st.session_state.messages.append(new_message)

            # Show suggestions immediately for the new response
            from modules.ui_components import render_auto_suggestions
            render_auto_suggestions(new_message, llm=st.session_state.chatbot.llm)




if __name__ == "__main__":
    main()

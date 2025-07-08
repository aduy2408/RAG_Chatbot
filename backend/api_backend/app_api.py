import streamlit as st
import requests
import time
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.config import MOBILE_FRIENDLY_CSS, APP_HEADER_HTML, SYSTEM_MESSAGES, ChatbotConfig
from modules.ui_components import ( render_sidebar, render_chat_message,
    render_sources_expander, render_response_metadata, initialize_chat_history, render_chat_input, show_typing_indicator,
    render_error_message, render_success_message
)
from modules.utils import get_language_flag

# API Backend Configuration
API_BASE_URL = "http://localhost:8000"  

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API returned status code: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "API backend is not responding (timeout)."
    except Exception as e:
        return False, f"Error checking API health: {str(e)}"

def call_chat_api(message, auto_detect=True, preferred_language="vi", top_k=5):
    """Call the /chat API endpoint"""
    try:
        payload = {
            "message": message,
            "auto_detect": auto_detect,
            "preferred_language": preferred_language,
            "top_k": top_k
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=30 
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"API Error: {error_detail}"
    except requests.exceptions.ConnectionError:
        return False, "Lost connection to API backend."
    except Exception as e:
        return False, f"Error calling chat API: {str(e)}"

def call_suggestions_api(response_content, language):
    """Call the /suggestions API endpoint"""
    try:
        payload = {
            "response_content": response_content,
            "language": language
        }
        
        response = requests.post(
            f"{API_BASE_URL}/suggestions",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()["suggestions"]
        else:
            return []  # Return empty list if suggestions fail
            
    except Exception as e:
        st.error(f"Error getting suggestions: {str(e)}")
        return []

def render_auto_suggestions_api(message):
    """Render auto-suggestions using API backend"""
    # Don't show suggestions if one has been clicked
    if 'quick_query' in st.session_state and st.session_state.quick_query:
        return

    detected_language = message.get("detected_language", "en")

    # Get context-aware suggestions from API
    suggestions = call_suggestions_api(message["content"], detected_language)

    if suggestions:
        st.markdown("---")
        st.markdown("**Suggested follow-up questions:**" if detected_language == "en" else "**Câu hỏi gợi ý tiếp theo:**")

        # Create columns for suggestions
        cols = st.columns(min(len(suggestions), 3))
        for i, suggestion in enumerate(suggestions[:3]):  # Limit to 3 suggestions
            with cols[i % 3]:
                # Use message content hash + index for unique keys
                import hashlib
                message_hash = hashlib.md5(message["content"].encode()).hexdigest()[:8]
                unique_key = f"suggestion_api_{message_hash}_{i}"

                if st.button(
                    suggestion,
                    key=unique_key,
                    use_container_width=True,
                    type="secondary"
                ):
                    # Set the suggestion in session state and immediately rerun
                    st.session_state.quick_query = suggestion
                    st.rerun()

def main():
    """Main application function"""
    st.set_page_config(**ChatbotConfig.get_streamlit_config())
    
    # Apply custom CSS
    st.markdown(MOBILE_FRIENDLY_CSS, unsafe_allow_html=True)
    
    # Check API backend health
    api_healthy, health_info = check_api_health()
    if not api_healthy:
        render_error_message(f"API Backend Error: {health_info}")
        st.info("Make sure to start the API backend first:")
        st.code("python api_backend.py")
        st.stop()

    # Render header
    st.markdown(APP_HEADER_HTML, unsafe_allow_html=True)
    
    # Render sideba
    auto_detect, preferred_language = render_sidebar()
    
    # Initialize chat history
    initialize_chat_history()

    # Check for auto-suggestion clicks first
    suggestion_prompt = None
    if 'quick_query' in st.session_state and st.session_state.quick_query:
        suggestion_prompt = st.session_state.quick_query
        st.session_state.quick_query = None 

    # Always render chat input at the bottom
    chat_input_prompt = render_chat_input()

    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        # Show suggestions only for the last assistant message, and only when not processing new input
        is_last_assistant = (
            i == len(st.session_state.messages) - 1 and
            message["role"] == "assistant" and
            not (suggestion_prompt or chat_input_prompt)  
        )
        
        # Use API version for suggestions
        if message["role"] == "assistant" and is_last_assistant:
            with st.chat_message("assistant"):
                # Show language detection badge
                if "detected_language" in message:
                    lang_flag = get_language_flag(message["detected_language"])
                    st.markdown(f'<span class="language-badge">{lang_flag} {message["detected_language"].upper()}</span>', unsafe_allow_html=True)

                st.markdown(message["content"])

                # Show sources for assistant messages
                if message.get("sources"):
                    render_sources_expander(message["sources"])

                # Show auto-suggestions using API
                render_auto_suggestions_api(message)
        else:
            render_chat_message(message, show_suggestions=False)

    # Use suggestion if available, otherwise use chat input
    prompt = suggestion_prompt or chat_input_prompt

    # Process any input (quick query or typed input)
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response using API
        with st.chat_message("assistant"):
            with show_typing_indicator():
                # Call the chat API
                success, api_response = call_chat_api(
                    message=prompt,
                    auto_detect=auto_detect,
                    preferred_language=preferred_language,
                    top_k=ChatbotConfig.DEFAULT_TOP_K
                )

            if success:
                # Show language detection badge
                lang_flag = get_language_flag(api_response["detected_language"])
                st.markdown(f'<span class="language-badge">{lang_flag} {api_response["detected_language"].upper()}</span>', unsafe_allow_html=True)

                # Display the answer
                st.markdown(api_response["answer"])

                # Show response metadata
                render_response_metadata(
                    api_response.get("response_time", 0), 
                    api_response["num_sources"], 
                    api_response["sources"]
                )

                # Show sources
                if api_response.get("sources"):
                    render_sources_expander(api_response["sources"])

                # Add assistant message to chat history
                new_message = {
                    "role": "assistant",
                    "content": api_response["answer"],
                    "sources": api_response.get("sources", []),
                    "detected_language": api_response["detected_language"],
                    "response_time": api_response.get("response_time", 0),
                    "num_sources": api_response["num_sources"]
                }
                st.session_state.messages.append(new_message)

                # Show suggestions immediately for the new response
                render_auto_suggestions_api(new_message)
            else:
                # Show error message
                render_error_message(f"Failed to get response: {api_response}")

if __name__ == "__main__":
    main()


import streamlit as st
from .utils import get_language_flag, get_context_suggestions
from .config import ChatbotConfig
import hashlib


def render_sidebar():
    with st.sidebar:
        st.title("Configuration")

        # Language settings
        st.subheader("Language")
        language_option = st.selectbox(
            "Language preference",
            ["Auto-detect", "Vietnamese", "English"],
            index=0,  # Default to Auto-detect
            key="sidebar_language_option",
            help="Choose how the chatbot should handle language detection"
        )

        # Convert selection to parameters
        if language_option == "Auto-detect":
            auto_detect = True
            language_code = ChatbotConfig.DEFAULT_LANGUAGE 
        elif language_option == "Vietnamese":
            auto_detect = False
            language_code = "vi"
        else:  # English
            auto_detect = False
            language_code = "en"


        # Actions
        render_sidebar_actions()

    return auto_detect, language_code


def render_sidebar_actions():
    """Render sidebar action buttons"""
    st.subheader("Actions")
    
    if st.button("Clear Chat History", type="secondary", use_container_width=True, key="sidebar_clear_chat"):
        st.session_state.messages = []
        if 'show_stats' in st.session_state:
            del st.session_state.show_stats
        st.rerun()


def render_chat_message(message, show_suggestions=False):
    """Render a single chat message"""
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            # Show language detection badge
            if "detected_language" in message:
                lang_flag = get_language_flag(message["detected_language"])
                st.markdown(f'<span class="language-badge">{lang_flag} {message["detected_language"].upper()}</span>', unsafe_allow_html=True)

        st.markdown(message["content"])

        # Show sources for assistant messages
        if message["role"] == "assistant" and message.get("sources"):
            render_sources_expander(message["sources"])

        # Show auto-suggestions only for the most recent assistant message
        if message["role"] == "assistant" and show_suggestions:
            render_auto_suggestions(message)


def render_auto_suggestions(message):
    """Render auto-suggestions based on the assistant's response"""
    # Don't show suggestions if one has been clicked
    if 'quick_query' in st.session_state and st.session_state.quick_query:
        return

    detected_language = message.get("detected_language", "en")

    # Get context-aware suggestions based on the response content
    suggestions = get_context_suggestions(message["content"], detected_language)

    if suggestions:
        st.markdown("---")
        st.markdown("**Suggested follow-up questions:**" if detected_language == "en" else "**Câu hỏi gợi ý tiếp theo:**")

        # Create columns for suggestions
        cols = st.columns(min(len(suggestions), 3))
        for i, suggestion in enumerate(suggestions[:3]): 
            with cols[i % 3]:
                # Use message content hash + index for unique keys to avoid conflicts
                message_hash = hashlib.md5(message["content"].encode()).hexdigest()[:8]
                unique_key = f"suggestion_{message_hash}_{i}"

                if st.button(
                    suggestion,
                    key=unique_key,
                    use_container_width=True,
                    type="secondary"
                ):
                    # Set the suggestion in session state and immediately rerun
                    st.session_state.quick_query = suggestion
                    st.rerun()


def render_sources_expander(sources):
    """Render sources in an expandable section"""
    with st.expander(f"Sources ({len(sources)} documents)", expanded=False):
        for j, source in enumerate(sources, 1):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{j}. {source['title']}**")
                    if source.get('url'):
                        st.markdown(f"[{source['url']}]({source['url']})")
                
                with col2:
                    if source.get('contains_table'):
                        st.markdown("**Table**")
                    else:
                        st.markdown("**Text**")

                with col3:
                    st.markdown(f"{source.get('chunk_length', 0)} chars")
                
                # Show content preview
                if source.get('content_preview'):
                    with st.expander("👁️ Preview", expanded=False):
                        st.text(source['content_preview'])
                
                st.divider()


def render_response_metadata(response_time, num_sources, sources):
    """Render response metadata (time, sources, tables)"""
    col1, col2 = st.columns(2)

    with col1:
        st.caption(f"Response time: {response_time:.2f}s")

    with col2:
        tables_count = sum(1 for s in sources if s.get("contains_table"))
        st.caption(f"{num_sources} sources • {tables_count} tables")



def handle_quick_query():
    """Handle quick query selection and return it as input"""
    if hasattr(st.session_state, 'quick_query') and st.session_state.quick_query:
        # Get the query and clear it
        query = st.session_state.quick_query
        del st.session_state.quick_query
        # Return the query to be processed as input
        return query
    return None


def initialize_chat_history():
    if "messages" not in st.session_state:
        from .utils import create_welcome_message
        st.session_state.messages = []
        welcome_msg = create_welcome_message()
        st.session_state.messages.append(welcome_msg)


def render_chat_input():
    """Render chat input"""
    # Always render the chat input
    return st.chat_input("💬 Type your question here... / Nhập câu hỏi của bạn...")


def show_typing_indicator():
    """Show typing indicator"""
    return st.spinner("Thinking... / Đang suy nghĩ...")


def render_error_message(error):
    """Render error message"""
    st.error(error)


def render_success_message(message):
    """Render success message"""
    st.success(message)


def render_info_message(message):
    """Render info message"""
    st.info(message)

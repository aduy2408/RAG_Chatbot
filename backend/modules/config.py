import os
from dotenv import load_dotenv

# Load environment variables from backend directory
backend_dir = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)


class ChatbotConfig:
    """Configuration class for APEC Chatbot"""
    
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
    LLM_MODEL = "gemini-2.0-flash"
    LLM_TEMPERATURE = 0.1
    
    # Vector Database Configuration
    VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db_langchain_e5")
    DEFAULT_TOP_K = 5
    DEFAULT_SEARCH_TYPE = "similarity"
    
    # UI Configuration
    APP_TITLE = "APEC 2025 Korea Chatbot"
    APP_ICON = ""
    DEFAULT_PORT = 8501
    DEFAULT_HOST = "0.0.0.0"
    
    # Language Configuration
    SUPPORTED_LANGUAGES = ["vi", "en"]
    DEFAULT_LANGUAGE = "vi"
    AUTO_DETECT_DEFAULT = True
    
    # Chat Configuration
    MAX_CHAT_HISTORY = 100
    SHOW_SOURCES_DEFAULT = True
    ENABLE_QUICK_REPLIES = True
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GOOGLE_API_KEY:
            return False, "GOOGLE_API_KEY not found in environment variables"
        
        if not os.path.exists(cls.VECTOR_DB_PATH):
            return False, f"Vector database not found at {cls.VECTOR_DB_PATH}"
        
        return True, "Configuration is valid"
    
    @classmethod
    def get_streamlit_config(cls):
        """Get Streamlit page configuration"""
        return {
            "page_title": cls.APP_TITLE,
            "page_icon": cls.APP_ICON,
            "layout": "wide",
            "initial_sidebar_state": "expanded"
        }
    
    @classmethod
    def get_model_settings_range(cls):
        """Get ranges for model settings sliders"""
        return {
            "top_k": {
                "min_value": 1,
                "max_value": 10,
                "value": cls.DEFAULT_TOP_K,
                "help": "More sources provide more context but may slow down responses"
            },
            "temperature": {
                "min_value": 0.0,
                "max_value": 1.0,
                "value": cls.LLM_TEMPERATURE,
                "step": 0.1,
                "help": "Higher values make responses more creative but less focused"
            }
        }


# CSS Styles for the application
MOBILE_FRIENDLY_CSS = """
<style>
/*Design */
.main-header {
    text-align: center;
    padding: 1.5rem 1rem;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3f51b5 100%);
    color: white;
    border-radius: 15px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Chat message styling */
.chat-message {
    padding: 1rem;
    border-radius: 15px;
    margin: 0.5rem 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-width: 100%;
    word-wrap: break-word;
}

.user-message {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-left: 4px solid #2196f3;
    margin-left: 10%;
}

.assistant-message {
    background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    border-left: 4px solid #9c27b0;
    margin-right: 10%;
}



/* Auto-suggestion buttons */
.suggestion-btn {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    color: #495057;
    border: 1px solid #dee2e6;
    padding: 0.5rem 0.75rem;
    border-radius: 15px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.3s ease;
    margin: 0.25rem;
    text-align: center;
}

.suggestion-btn:hover {
    background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Language badge */
.language-badge {
    display: inline-block;
    padding: 0.4rem 0.8rem;
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    color: white;
    border-radius: 20px;
    font-size: 0.8rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Compact quick reply buttons */
div[data-testid="column"] .stButton > button {
    height: 2.2rem !important;
    font-size: 0.8rem !important;
    padding: 0.2rem 0.4rem !important;
    margin-bottom: 0.3rem !important;
    border-radius: 8px !important;
}

/* Source cards */
.source-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
    transition: all 0.3s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.source-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

/* Mobile optimizations */
@media (max-width: 768px) {
    .main-header {
        padding: 1rem 0.5rem;
        margin-bottom: 1rem;
    }
    
    .main-header h1 {
        font-size: 1.5rem !important;
    }
    
    .chat-message {
        padding: 0.75rem;
        margin: 0.25rem 0;
    }
    
    .user-message {
        margin-left: 5%;
    }

    .assistant-message {
        margin-right: 5%;
    }
    
    .quick-reply-btn {
        padding: 0.6rem 0.8rem;
        font-size: 0.8rem;
        min-width: 100px;
    }
}

/* Sidebar optimizations */
.sidebar .stSelectbox, .sidebar .stSlider {
    margin-bottom: 1rem;
}



/* Chat input styling */
.stChatInput > div > div > div > div {
    border-radius: 25px !important;
    border: 2px solid #e0e0e0 !important;
}

.stChatInput > div > div > div > div:focus-within {
    border-color: #2196f3 !important;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2) !important;
}
</style>
"""

# App header HTML
APP_HEADER_HTML = """
<div class="main-header">
    <h1>APEC 2025 Chatbot</h1>
    <p>Your intelligent assistant for APEC 2025 events, schedules, and information</p>
</div>
"""

# Footer HTML
APP_FOOTER_HTML = """
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    APEC 2025 Korea Chatbot
</div>
"""

SYSTEM_MESSAGES = {
    "loading": "Initializing APEC Chatbot...",
    "thinking": "Thinking... / Đang suy nghĩ...",
    "error": "An error occurred. Please try again.",
    "no_api_key": "Google API key not found. Please check your .env file.",
    "no_vector_store": "Vector db not found. Please run the RAG setup first."
}

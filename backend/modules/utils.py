import langdetect
import os
from pathlib import Path


def detect_language(text):
    try:
        detected = langdetect.detect(text)
        vietnamese_chars = set('àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ')
        has_vietnamese = any(char in vietnamese_chars for char in text.lower())
        
        if has_vietnamese or detected == 'vi':
            return 'vi'
        else:
            return 'en'
    except:
        return 'en'


def get_language_flag(language):    
    return "🇻🇳" if language == "vi" else "🇺🇸"


def create_welcome_message():
    """Create the welcome message for new users"""
    return {
        "role": "assistant",
        "content": """**Chào mừng bạn đến với APEC 2025 Korea Chatbot!**

Tôi có thể giúp bạn:
- Tìm hiểu lịch trình các sự kiện APEC 2025
- Thông tin về địa điểm tổ chức
- Chi tiết về các cuộc họp và hội nghị
- Thông tin tổng quan về APEC

**Welcome to APEC 2025 Korea Chatbot!**

I can help you with:
- APEC 2025 event schedules
- Venue information
- Meeting and conference details
- General APEC information

Hãy đặt câu hỏi bằng tiếng Việt hoặc tiếng Anh! / Ask me anything in Vietnamese or English!""",
        "sources": [],
        "detected_language": "vi"
    }


def validate_environment():
    """Validate that the environment is properly set up"""
    # Check for .env file in backend directory
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    env_file = Path(os.path.join(backend_dir, '.env'))
    if not env_file.exists():
        return False, ".env file not found! Create a .env file with your Google API key."

    # Load environment variables from the backend directory
    from dotenv import load_dotenv
    load_dotenv(env_file)

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return False, "GOOGLE_API_KEY not found in environment variables!"

    # Check for vector store in backend directory
    vector_store_path = Path(os.path.join(backend_dir, 'chroma_db_langchain_e5'))
    if not vector_store_path.exists():
        return False, "Vector store not found! Please run the RAG setup first."

    return True, "Environment validation passed"


def get_context_suggestions(response_content, language):
    """Generate context-aware suggestions based on the assistant's response"""
    response_lower = response_content.lower()

    # Define suggestion patterns based on content keywords
    if language == "vi":
        suggestions_map = {
            # Event/Schedule related
            ("sự kiện", "lịch", "tháng 5", "cuộc họp"): [
                "Chi tiết về các cuộc họp quan trọng nhất?",
                "Ai sẽ tham dự các sự kiện này?",
                "Làm thế nào để đăng ký tham gia?"
            ],
            # Location related
            ("địa điểm", "nơi", "tổ chức", "venue"): [
                "Hướng dẫn đến các địa điểm này?",
                "Có dịch vụ đưa đón không?",
                "Thông tin về chỗ ở gần đó?"
            ],
            # APEC general
            ("apec", "tổ chức", "mục tiêu"): [
                "Lịch sử của APEC là gì?",
                "Các thành viên APEC hiện tại?",
                "Vai trò của Hàn Quốc trong APEC 2025?"
            ],
            # Business/Economic
            ("kinh tế", "thương mại", "doanh nghiệp"): [
                "Cơ hội kinh doanh từ APEC 2025?",
                "Các thỏa thuận thương mại mới?",
                "Tác động đến nền kinh tế khu vực?"
            ]
        }
    else:  # English
        suggestions_map = {
            # Event/Schedule related
            ("event", "schedule", "may", "meeting", "conference"): [
                "What are the most important meetings?",
                "Who will attend these events?",
                "How to register for participation?"
            ],
            # Location related
            ("venue", "location", "place", "where"): [
                "How to get to these venues?",
                "Is transportation provided?",
                "Accommodation options nearby?"
            ],
            # APEC general
            ("apec", "organization", "goal", "objective"): [
                "What is the history of APEC?",
                "Current APEC member countries?",
                "Korea's role in APEC 2025?"
            ],
            # Business/Economic
            ("economic", "trade", "business", "commerce"): [
                "Business opportunities from APEC 2025?",
                "New trade agreements?",
                "Impact on regional economy?"
            ]
        }

    # Find matching suggestions based on content
    for keywords, suggestions in suggestions_map.items():
        if any(keyword in response_lower for keyword in keywords):
            return suggestions

    # Default suggestions if no specific match
    if language == "vi":
        return [
            "Cho tôi biết thêm chi tiết?",
            "Có thông tin nào khác không?",
            "Tôi có thể hỏi gì tiếp theo?"
        ]
    else:
        return [
            "Tell me more details?",
            "Any other information?",
            "What else can I ask?"
        ]

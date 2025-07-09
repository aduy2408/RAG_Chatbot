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


def get_hardcoded_suggestions(response_content, language):
    """Generate hardcoded context-aware suggestions based on the assistant's response"""
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


def generate_llm_suggestions(response_content, language, llm=None):
    """Generate suggestions using LLM based on the assistant's response"""
    if not llm:
        return []

    try:
        if language == "vi":
            prompt = f"""Dựa trên phản hồi sau về APEC 2025 Korea, hãy tạo ra 2-3 câu hỏi tiếp theo ngắn gọn và hữu ích mà người dùng có thể quan tâm:

Phản hồi: {response_content[:500]}...

Yêu cầu:
- Tạo 2-3 câu hỏi ngắn gọn (tối đa 10 từ mỗi câu)
- Câu hỏi phải liên quan đến nội dung phản hồi
- Tập trung vào APEC 2025, sự kiện, địa điểm, thủ tục
- Chỉ trả về danh sách câu hỏi, mỗi câu một dòng
- Không giải thích thêm"""
        else:
            prompt = f"""Based on the following response about APEC 2025 Korea, generate 2-3 short and useful follow-up questions that users might be interested in:

Response: {response_content[:500]}...

Requirements:
- Generate 2-3 concise questions (max 10 words each)
- Questions must be related to the response content
- Focus on APEC 2025, events, venues, procedures
- Only return the list of questions, one per line
- No additional explanations"""

        # Use the LLM to generate suggestions
        result = llm.invoke(prompt)

        # Parse result to extract questions
        suggestions = []
        if hasattr(result, 'content'):
            content = result.content
        else:
            content = str(result)

        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Remove bullet points, numbers, quotes
            line = line.lstrip('•-*123456789. "\'')
            line = line.rstrip('"\'')

            if line.startswith('- '):
                line = line[2:]
            if line.startswith('* '):
                line = line[2:]

            # Only keep lines that look like questions and are reasonable length
            if line and len(line) > 5 and len(line) < 100 and '?' in line:
                cleaned_line = line.replace('\n', ' ').replace('\r', ' ').strip()
                if cleaned_line:
                    suggestions.append(cleaned_line)

        return suggestions[:3]  # Limit to 3 suggestions

    except Exception as e:
        return []


def get_context_suggestions(response_content, language, llm=None):
    """Generate combined suggestions: hardcoded + LLM-generated"""
    # Get hardcoded suggestions
    hardcoded_suggestions = get_hardcoded_suggestions(response_content, language)

    # Get LLM-generated suggestions
    llm_suggestions = generate_llm_suggestions(response_content, language, llm)

    # Combine suggestions
    combined_suggestions = []

    # Add hardcoded suggestions first (up to 2)
    combined_suggestions.extend(hardcoded_suggestions[:2])

    # Add LLM suggestions to fill remaining slots wit validation
    for suggestion in llm_suggestions:
        # Validate that the suggestion is clean and usable
        if (suggestion not in combined_suggestions and
            len(combined_suggestions) < 3 and
            suggestion and
            len(suggestion.strip()) > 5 and
            len(suggestion.strip()) < 100):
            combined_suggestions.append(suggestion.strip())

    for suggestion in hardcoded_suggestions[2:]:
        if len(combined_suggestions) < 3:
            combined_suggestions.append(suggestion)

    return combined_suggestions[:3]  

import os

# RAG components
from sentence_transformers import SentenceTransformer

# Langchain components
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

from .utils import detect_language


class APECChatbot:    
    def __init__(self, api_key, persist_directory="./chroma_db_langchain_e5"):
        self.api_key = api_key
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.llm = None
        self.embedding_model = None
        self.embeddings = None
        self.setup_models()
        
    def setup_models(self):
        try:
            self.embedding_model = SentenceTransformer("intfloat/multilingual-e5-large")
            
            # Langchain wrapper for embeddings
            self.embeddings = SentenceTransformerEmbeddings(model_name="intfloat/multilingual-e5-large")
            
            # Load vector store
            if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
                self.vectorstore = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
            else:
                raise Exception("Vector store not found! Please run the RAG setup first.")
            
            #Gemini LLM
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.1,
                convert_system_message_to_human=True,
                google_api_key=self.api_key
            )
            
        except Exception as e:
            raise Exception(f"Error initializing models: {str(e)}")
    
    def get_language_specific_prompt(self, language):
        if language == 'vi':
            vietnamese_template = """Bạn là trợ lý AI chuyên về APEC 2025 Korea và các thông tin liên quan đến du lịch, văn hóa Việt Nam.

            Hướng dẫn:
            - Ưu tiên sử dụng thông tin được cung cấp trong ngữ cảnh để trả lời câu hỏi một cách chính xác
            - Khi trình bày dữ liệu bảng, định dạng rõ ràng và dễ đọc
            - Bao gồm các chi tiết cụ thể như ngày tháng, địa điểm và tên sự kiện
            - Nếu ngữ cảnh chứa nhiều mục liên quan, hãy liệt kê tất cả
            - Nếu câu hỏi về các chủ đề như thủ tục nhập cảnh, visa, y tế, văn hóa Việt Nam, Phú Quốc mà không có trong ngữ cảnh, hãy cung cấp thông tin hữu ích dựa trên kiến thức chung
            - Đối với câu hỏi về APEC 2025 Korea mà không tìm thấy trong ngữ cảnh, hãy nói rõ ràng và gợi ý liên hệ ban tổ chức
            - Luôn trả lời một cách hữu ích và thân thiện
            - Trả lời bằng tiếng Việt

            Ngữ cảnh:
            {context}

            Câu hỏi: {question}

            Trả lời:"""

            return PromptTemplate(template=vietnamese_template,input_variables=["context", "question"])
        else:
            english_template = """You are an expert AI assistant specializing in APEC 2025 Korea information and related travel, cultural information about Vietnam.

            Instructions:
            - Prioritize using the provided context to answer questions accurately
            - When presenting table data, format it clearly and readably
            - Include specific details like dates, venues, and event names
            - If the context contains multiple relevant items, list them all
            - For questions about immigration procedures, visa, healthcare, Vietnamese culture, Phu Quoc that are not in the context, provide helpful information based on general knowledge
            - For APEC 2025 Korea specific questions not found in context, clearly state this and suggest contacting the organizers
            - Always respond helpfully and in a friendly manner
            - Maintain accuracy of all factual information

            Context:
            {context}

            Question: {question}

            Answer:"""

            return PromptTemplate(template=english_template,input_variables=["context", "question"])
    
    def query(self, question, top_k=5, auto_detect=True, preferred_language="vi", **kwargs):
        try:
            # Detect language based on settings
            if auto_detect:
                detected_language = detect_language(question)
            else:
                detected_language = preferred_language
            
            # Get language-specific prompt
            language_prompt = self.get_language_specific_prompt(detected_language)
            
            # Create temporary chain with language-specific prompt
            temp_qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_type=kwargs.get("search_type", "similarity"),
                    search_kwargs={"k": top_k}
                ),
                chain_type_kwargs={"prompt": language_prompt},
                return_source_documents=True
            )
            
            search_question = f"query: {question}"
            result = temp_qa_chain({"query": search_question})
            
            # Process sources
            sources = []
            for doc in result["source_documents"]:
                source_info = {
                    "title": doc.metadata.get("title", "Unknown"),
                    "url": doc.metadata.get("url", ""),
                    "contains_table": doc.metadata.get("contains_table", False),
                    "chunk_length": doc.metadata.get("chunk_length", 0),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                sources.append(source_info)
            
            response = {
                "answer": result["result"],
                "sources": sources,
                "num_sources": len(sources),
                "detected_language": detected_language
            }
            
            return response
            
        except Exception as e:
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "sources": [],
                "num_sources": 0,
                "detected_language": "en"
            }
    
    def get_collection_count(self):
        try:
            if self.vectorstore:
                return self.vectorstore._collection.count()
            return 0
        except:
            return 0
    
    def is_ready(self):
        """Check if the chatbot is ready to use"""
        return all([
            self.vectorstore is not None,
            self.llm is not None,
            self.embedding_model is not None,
            self.embeddings is not None
        ])

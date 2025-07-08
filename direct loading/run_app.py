
import os
import sys
import subprocess
from pathlib import Path

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))


def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'langchain',
        'chromadb',
        'sentence-transformers',
        'langchain-google-genai',
        'dotenv',
        'langdetect'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_environment():
    # Check for .env file in backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
    env_file = Path(os.path.join(backend_dir, '.env'))

    if not env_file.exists():
        print(".env file not found!")
        print("Create a .env file in the backend directory with your Google API key:")
        print("GOOGLE_API_KEY=your_api_key_here")
        return False

    # Check for vector store in backend directory
    vector_store_path = Path(os.path.join(backend_dir, 'chroma_db_langchain_e5'))
    if not vector_store_path.exists():
        print("Vector store not found!")
        print("Please run the RAG setup first to create the vector store.")
        print("Check RAG_LLM_Integration.ipynb for setup instructions.")
        return False
    
    return True


def run_app():
    print("Starting APEC 2025 Korea Chatbot...")
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0'
        ])
    except Exception as e:
        print(f"Error running chatbot: {e}")


def main():
    print("Checking requirements...")
    if not check_requirements():
        sys.exit(1)

    print("All required packages found")

    print("Checking environment...")
    if not check_environment():
        sys.exit(1)

    print("Environment configured correctly")
    
    run_app()


if __name__ == "__main__":
    main()

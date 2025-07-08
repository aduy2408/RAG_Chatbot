import os
import sys
import subprocess
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'requests',
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
        print(f"pip install -r requirements_api.txt")
        return False
    
    return True

def check_environment():
    """Check environment setup"""
    # Check for .env file in backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), '..')
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

def start_api_server():
    print("Starting API Backend...")
    print("API: http://localhost:8000")
    
    try:
        # Change to backend/api_backend directory to run uvicorn
        api_backend_dir = os.path.dirname(__file__)
        os.chdir(api_backend_dir)

        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'api_backend:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
    except Exception as e:
        print(f"Error running API backend: {e}")

def main():
    print("Checking requirements...")
    if not check_requirements():
        sys.exit(1)

    print("All required packages found")

    print("Checking environment...")
    if not check_environment():
        sys.exit(1)

    print("Environment configured correctly")
    
    start_api_server()

if __name__ == "__main__":
    main()

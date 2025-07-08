import os
import sys
import subprocess
import requests
import time

def check_api_backend():
    """Check if the API backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API returned status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to API backend"
    except Exception as e:
        return False, str(e)

def wait_for_api_backend(max_wait=30):
    print("Checking if API backend is running...")

    for i in range(max_wait):
        is_ready, info = check_api_backend()
        if is_ready:
            print("API backend is ready!")
            if isinstance(info, dict):
                print(f"Vector store: {info.get('vector_store_count', 0)} documents")
            return True

        if i == 0:
            print("Waiting for API backend to start...")
            print("Make sure to run: python start_api_backend.py")

        time.sleep(1)

    return False

def start_streamlit_app():
    """Start the Streamlit frontend"""
    import os
import sys
import subprocess
import requests
import time

def check_api_backend():
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API returned status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to API backend"
    except Exception as e:
        return False, str(e)

def wait_for_api_backend(max_wait=30):
    print("Checking if API backend is running...")

    for i in range(max_wait):
        is_ready, info = check_api_backend()
        if is_ready:
            print("API backend is ready!")
            if isinstance(info, dict):
                print(f"Vector store: {info.get('vector_store_count', 0)} documents")
            return True

        if i == 0:
            print("Waiting for API backend to start...")
            print("Make sure to run: python backend/api_backend/start_api_backend.py")

        time.sleep(1)

    return False

def start_streamlit_app():
    print("Starting APEC 2025 RAG Chatbot Frontend...")
    print("http://localhost:8502")

    try:
        # Change to backend/api_backend directory to run the frontend
        api_backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'api_backend')

        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            os.path.join(api_backend_dir, 'app_api.py'),
            '--server.port', '8502',
            '--server.address', '0.0.0.0'
        ])
    except Exception as e:
        print(f"Error running frontend: {e}")

def main():
    if not wait_for_api_backend():
        print("API backend is not running!")
        sys.exit(1)

    start_streamlit_app()

if __name__ == "__main__":
    main()
    print("-" * 50)

    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app_api.py',
            '--server.port', '8502',
            '--server.address', '0.0.0.0'
        ])
    except Exception as e:
        print(f"Error running frontend: {e}")

def main():
    if not wait_for_api_backend():
        print("API backend is not running!")
        sys.exit(1)
    
    start_streamlit_app()

if __name__ == "__main__":
    main()

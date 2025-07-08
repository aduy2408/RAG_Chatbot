#!/usr/bin/env python3
"""
Main startup script for APEC 2025 RAG Chatbot API
Run this from the root directory
"""

import os
import sys
import subprocess

def main():
    print("Starting APEC 2025 RAG Chatbot API Backend...")
    
    # Change to backend/api_backend directory
    api_backend_dir = os.path.join(os.path.dirname(__file__), 'backend', 'api_backend')
    
    try:
        subprocess.run([
            sys.executable, 
            os.path.join(api_backend_dir, 'start_api_backend.py')
        ])
    except Exception as e:
        print(f"Error starting API backend: {e}")

if __name__ == "__main__":
    main()

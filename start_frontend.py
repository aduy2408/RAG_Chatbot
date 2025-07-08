#!/usr/bin/env python3
"""
Main startup script for APEC 2025 RAG Chatbot Frontend
Run this from the root directory
"""

import os
import sys
import subprocess

def main():
    print("Starting APEC 2025 RAG Chatbot Frontend...")
    
    # Use the demo frontend starter
    demo_dir = os.path.join(os.path.dirname(__file__), 'demo')
    
    try:
        subprocess.run([
            sys.executable, 
            os.path.join(demo_dir, 'start_frontend.py')
        ])
    except Exception as e:
        print(f"Error starting frontend: {e}")

if __name__ == "__main__":
    main()

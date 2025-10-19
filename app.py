#!/usr/bin/env python3
"""
Unified Pentest Vulnerability Report Generator
This script runs both the backend API and serves the frontend
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import langchain_ollama
        import reportlab
        import markdown
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_ollama():
    """Check if OLLAMA is running and has the required model"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'llama3.2:3b' in result.stdout:
            print("✅ OLLAMA is running with llama3.2:3b model")
            return True
        else:
            print("⚠️  OLLAMA not running or model not found")
            print("   To enable AI features:")
            print("   1. Install OLLAMA: https://ollama.ai/")
            print("   2. Run: ollama serve")
            print("   3. Run: ollama pull llama3.2:3b")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  OLLAMA not found or not responding")
        print("   AI features will be disabled")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    try:
        subprocess.run([sys.executable, 'backend.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🔒 Pentest Vulnerability Report Generator")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend.py'):
        print("❌ Please run this script from the project directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check OLLAMA (optional)
    ai_available = check_ollama()
    
    if ai_available:
        print("🤖 AI features enabled")
    else:
        print("⚠️  AI features disabled - application will work with manual input")
    
    print("\n📱 Application will be available at: http://localhost:8001")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    # Start the backend
    try:
        start_backend()
    except KeyboardInterrupt:
        print("\n👋 Application stopped")

if __name__ == "__main__":
    main()
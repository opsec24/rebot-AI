#!/usr/bin/env python3
"""
Pentest Vulnerability Report Generator
Run this script to start the application
"""

import subprocess
import sys
import os
import time

def check_ollama():
    """Check if OLLAMA is running and has llama3.2:3b model"""
    try:
        # Check if ollama is running
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ OLLAMA is not running. Please start OLLAMA first:")
            print("   ollama serve")
            return False
        
        # Check if llama3.2:3b model is available
        if 'llama3.2:3b' not in result.stdout:
            print("❌ LLaMA 3.2 3B model not found. Installing...")
            install_result = subprocess.run(['ollama', 'pull', 'llama3.2:3b'], 
                                          capture_output=True, text=True)
            if install_result.returncode != 0:
                print("❌ Failed to install LLaMA 3.2 3B model")
                return False
            print("✅ LLaMA 3.2 3B model installed successfully")
        
        print("✅ OLLAMA is running with LLaMA 3.2 3B model")
        return True
        
    except FileNotFoundError:
        print("❌ OLLAMA is not installed. Please install OLLAMA first:")
        print("   Visit: https://ollama.ai/")
        return False

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting Pentest Vulnerability Report Generator...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, 'backend.py'])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")

def main():
    """Main function"""
    print("🔒 Pentest Vulnerability Report Generator")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend.py'):
        print("❌ Please run this script from the project directory")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Check OLLAMA
    if not check_ollama():
        print("\n⚠️  You can still run the application, but AI features won't work")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()

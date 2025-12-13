#!/usr/bin/env python3
"""
Setup script for the Multi-Agent Content Generation System
Now using Google Gemini API (Free Tier)
"""

import os
import sys
import subprocess

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ recommended, found {version.major}.{version.minor}")
        print("   The system may still work with Python 3.10+")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required packages for Gemini"""
    print("\n📦 Installing Gemini dependencies...")
    
    # First check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found. Creating basic one...")
        basic_reqs = """langchain>=0.1.0
langchain-google-genai>=0.0.3
langgraph>=0.0.26
langchain-community>=0.0.10
pydantic>=2.5.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
tenacity>=8.2.2"""
        
        with open("requirements.txt", "w") as f:
            f.write(basic_reqs)
        print("✅ Created requirements.txt")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Gemini dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("\nTrying manual installation...")
        
        # Try manual installation of core packages
        packages = [
            "langchain",
            "langchain-google-genai",
            "google-generativeai",
            "langgraph",
            "pydantic",
            "python-dotenv"
        ]
        
        for package in packages:
            try:
                print(f"  Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except:
                print(f"  ⚠️  Could not install {package}")
                continue
        
        return True

def setup_environment():
    """Setup environment file for Gemini"""
    print("\n⚙️  Setting up Gemini environment...")
    
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ {env_file} already exists")
        # Check if it has Gemini keys
        with open(env_file, "r") as f:
            content = f.read()
            if "GOOGLE_API_KEY" not in content:
                print("⚠️  .env doesn't have GOOGLE_API_KEY")
                print("   Consider updating it for Gemini API")
        return True
    
    # Create .env for Gemini
    template = """# Google Gemini Configuration (FREE TIER)
GOOGLE_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-flash
TEMPERATURE=0.0

# Optional: Fallback provider
# PREFERRED_PROVIDER=google

# Logging
LOG_LEVEL=INFO

# Note: Get free Gemini API key from:
# https://makersuite.google.com/app/apikey
"""
    
    with open(env_file, "w") as f:
        f.write(template)
    
    print(f"✅ Created {env_file} for Gemini")
    print(f"🔑 Get FREE API key from: https://makersuite.google.com/app/apikey")
    print(f"📝 Edit {env_file} and add your Gemini API key")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["outputs", "docs", "tests", "src/core", "src/agents", "src/orchestration", "src/utils"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}/")
    
    return True

def verify_gemini_installation():
    """Verify Gemini packages are installed"""
    print("\n🔍 Verifying Gemini installation...")
    
    test_code = """
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

print("✅ google.generativeai imported successfully")
print("✅ langchain_google_genai imported successfully")

# Test basic configuration
try:
    genai.configure(api_key="test_key")
    print("✅ Gemini configuration test passed")
except Exception as e:
    print(f"⚠️  Configuration test: {type(e).__name__}")

print("🎉 Gemini setup verification complete!")
"""
    
    try:
        # Write test script
        with open("test_gemini_setup.py", "w") as f:
            f.write(test_code)
        
        # Run test
        result = subprocess.run([sys.executable, "test_gemini_setup.py"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            print("✅ Gemini packages verified")
        else:
            print("❌ Gemini verification failed")
            print(result.stderr)
        
        # Clean up
        if os.path.exists("test_gemini_setup.py"):
            os.remove("test_gemini_setup.py")
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    return True

def provide_instructions():
    """Provide next steps instructions"""
    print("\n" + "="*60)
    print("✅ Gemini Setup Complete!")
    print("="*60)
    
    print("\n🎯 Next Steps:")
    print("1. 🔑 Get FREE Gemini API key from:")
    print("   https://makersuite.google.com/app/apikey")
    print("2. 📝 Edit .env file and add your GOOGLE_API_KEY")
    print("3. 🧪 Test the setup: python verify_llm.py")
    print("4. 🚀 Run the system: python run.py")
    print("5. 📁 Check outputs in outputs/ directory")
    
    print("\n📋 Quick Commands:")
    print("  # Test imports")
    print("  python test_imports.py")
    print("")
    print("  # Test Gemini API")
    print("  python verify_llm.py")
    print("")
    print("  # Run full system")
    print("  python run.py")
    print("")
    print("  # Run individual agents")
    print("  python -m src.utils.main_agents")
    
    print("\n🔧 Troubleshooting:")
    print("• If you get API errors: Check GOOGLE_API_KEY in .env")
    print("• If imports fail: Run 'pip install -r requirements.txt'")
    print("• If LangGraph fails: Use 'python -m src.utils.main_agents'")
    
    print("\n" + "="*60)
    print("🧠 Powered by Google Gemini API (Free Tier)")
    print("="*60)

def main():
    """Main setup function for Gemini"""
    print("="*60)
    print("Multi-Agent Content Generation System - Setup")
    print("GOOGLE GEMINI API VERSION (FREE)")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️  Continuing with manual setup...")
    
    # Setup environment
    setup_environment()
    
    # Create directories
    create_directories()
    
    # Verify installation
    verify_gemini_installation()
    
    # Provide instructions
    provide_instructions()

if __name__ == "__main__":
    main()
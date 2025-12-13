#!/usr/bin/env python3
"""
Main runner script for the LangChain Multi-Agent Content Generation System
Now using Google Gemini API
"""

import sys
import os

def verify_llm_environment():
    """Verify that Gemini environment is properly setup"""
    print("\n🔬 Verifying Gemini Environment...")
    
    try:
        import google.generativeai as genai
        import os
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_google_api_key_here":
            print("❌ ERROR: Invalid Google API key in .env file")
            print("Please update .env with your Gemini API key from:")
            print("https://makersuite.google.com/app/apikey")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Try different Gemini models (all free)
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        
        for model in models_to_try:
            try:
                print(f"  Testing model: {model}...")
                gemini_model = genai.GenerativeModel(model)
                test_response = gemini_model.generate_content(
                    "test",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=5
                    )
                )
                
                if test_response.text:
                    print(f"✅ Gemini API is working correctly with {model}")
                    
                    # Update .env with working model
                    with open('.env', 'r') as f:
                        env_content = f.read()
                    
                    # Update MODEL_NAME if needed
                    current_model = os.getenv("MODEL_NAME", "gemini-1.5-flash")
                    if model != current_model:
                        env_content = env_content.replace(
                            f"MODEL_NAME={current_model}",
                            f"MODEL_NAME={model}"
                        )
                        with open('.env', 'w') as f:
                            f.write(env_content)
                        print(f"  Updated .env to use {model}")
                    
                    return True
                    
            except Exception as e:
                print(f"  Model {model} failed: {e}")
                continue
        
        print("❌ All Gemini models failed.")
        print("   Please check:")
        print("   1. GOOGLE_API_KEY in .env file")
        print("   2. Get a free key from: https://makersuite.google.com/app/apikey")
        return False
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'langchain',
        'langchain_google_genai',  # Changed from langchain_openai
        'langgraph',
        'pydantic',
        'google.generativeai'      # Changed from openai
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'google.generativeai':
                __import__('google.generativeai')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    return missing

def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_file):
        print("❌ ERROR: .env file not found!")
        print(f"Expected at: {env_file}")
        print("\nPlease create .env file with:")
        print("GOOGLE_API_KEY=your_gemini_api_key_here")
        print("MODEL_NAME=gemini-1.5-flash")
        print("TEMPERATURE=0.0")
        return False
    
    # Check if API key is present
    with open(env_file, 'r') as f:
        content = f.read()
        if 'GOOGLE_API_KEY' not in content or 'your_google_api_key_here' in content:
            print("❌ ERROR: GOOGLE_API_KEY not properly configured in .env file!")
            print("Get a free Gemini API key from: https://makersuite.google.com/app/apikey")
            return False
    
    return True

def setup_output_directory():
    """Create output directory if it doesn't exist"""
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ Created output directory: {output_dir}")
    return output_dir

def display_banner():
    """Display system banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🚀 Multi-Agent Content Generation System                   ║
    ║   🔧 Kasparro Applied AI Engineer Challenge                  ║
    ║   🏗️  Built with LangChain + LangGraph + Gemini              ║
    ║   🆓 Powered by Free Google Gemini API                       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main execution function"""
    
    # Display banner
    display_banner()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing_packages = check_dependencies()
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("\nPlease install with: pip install -r requirements.txt")
        sys.exit(1)
    print("✅ All dependencies installed")
    
    # Check environment file
    print("\n🔧 Checking configuration...")
    if not check_env_file():
        sys.exit(1)
    print("✅ Environment configuration OK")
    
    # Verify Gemini environment
    if not verify_llm_environment():
        print("\n⚠️  Gemini environment verification failed")
        print("The system may not generate LLM-driven content")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    
    # Setup output directory
    print("\n📁 Setting up directories...")
    output_dir = setup_output_directory()
    print(f"✅ Output directory: {output_dir}")
    
    # Import and run the main system
    try:
        print("\n" + "="*60)
        print("🚀 Starting LangChain Multi-Agent System with Gemini")
        print("="*60 + "\n")
        
        from src.main import main as run_system
        run_system()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nMake sure you're in the correct directory and src/ exists")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Execution interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ System execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
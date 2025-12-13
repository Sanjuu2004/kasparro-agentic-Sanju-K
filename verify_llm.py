#!/usr/bin/env python3
"""
Verify that the system is actually using Gemini for content generation
"""

import json
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_gemini_response():
    """Test that Gemini API is working and returns LLM content"""
    print("Testing Gemini connectivity...")
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in .env file")
            return False, None
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Try available Gemini models (all free tier)
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        
        for model in models_to_try:
            try:
                print(f"  Trying model: {model}...")
                start = time.time()
                
                # Initialize the model
                gemini_model = genai.GenerativeModel(model)
                
                # Generate content
                response = gemini_model.generate_content(
                    "Write one sentence about skincare.",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=50
                    )
                )
                
                elapsed = time.time() - start
                
                if response.text:
                    print(f"✅ Gemini Response received using {model} in {elapsed:.2f} seconds")
                    print(f"Response: {response.text}")
                    
                    # Verify it's not template-based
                    if len(response.text) > 10 and ' ' in response.text:
                        print("✅ Content appears to be LLM-generated (not template)")
                        return True, model
                    else:
                        print("⚠️  Content may be template-based")
                        return True, model  # Still return True as API works
                else:
                    print(f"⚠️  No response text from {model}")
                    
            except Exception as e:
                print(f"  Model {model} failed: {e}")
                continue
        
        print("❌ All Gemini models failed")
        return False, None
        
    except Exception as e:
        print(f"❌ Gemini client error: {e}")
        return False, None

def verify_output_files():
    """Verify output files contain LLM-generated content"""
    print("\nVerifying output files...")
    
    required_files = ["faq.json", "product_page.json", "comparison_page.json"]
    
    for file in required_files:
        path = os.path.join("outputs", file)
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                size = os.path.getsize(path)
                
                print(f"\n📄 {file}:")
                print(f"  Size: {size} bytes")
                
                if file == "faq.json":
                    items = data.get('faq_items', [])
                    print(f"  FAQ Items: {len(items)}")
                    if items:
                        # Get first answer
                        first_item = items[0] if isinstance(items, list) else next(iter(items.values()))
                        answer = first_item.get('answer', '') if isinstance(first_item, dict) else str(first_item)
                        if len(answer) > 50 and ' ' in answer:
                            print("  ✅ FAQ answers appear LLM-generated")
                        else:
                            print("  ⚠️  FAQ answers may be template-based")
                            
                elif file == "comparison_page.json":
                    points = data.get('comparison_points', []) or data.get('points', [])
                    print(f"  Comparison Points: {len(points)}")
                    if len(points) >= 4:
                        print("  ✅ Detailed comparison (LLM likely used)")
                    else:
                        print("  ⚠️  Minimal comparison (may not be LLM-generated)")
                        
                elif file == "product_page.json":
                    # Check for rich content
                    has_sections = any(key in data for key in ['sections', 'benefits', 'ingredients', 'description'])
                    if has_sections:
                        print("  ✅ Product page has structured sections (LLM likely used)")
                    else:
                        print("  ⚠️  Product page may be template-based")
        else:
            print(f"\n❌ Missing: {file}")

def check_llm_usage_in_system():
    """Check if system is configured to use LLM"""
    print("\nChecking system configuration...")
    
    # Check config.py
    try:
        from src.config import Config
        config = Config()
        print(f"✅ Config loaded. Model: {config.model_name}")
        print(f"   Provider: Google Gemini")
        
        # Test the connection
        if config.test_llm_connection():
            return True
        else:
            print("❌ LLM connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Config error: {e}")
        print("   Make sure GOOGLE_API_KEY is in .env file")
        return False

def main():
    print("="*60)
    print("GEMINI LLM GENERATION VERIFICATION SCRIPT")
    print("="*60)
    
    # Check system configuration
    if not check_llm_usage_in_system():
        print("\n❌ System configuration error")
        print("   Please check your .env file and GOOGLE_API_KEY")
        return
    
    # Test API connectivity
    llm_working, model_used = test_gemini_response()
    if not llm_working:
        print("\n⚠️  Gemini connectivity test failed")
        print("   The system will use fallback/template content")
        
        response = input("\nContinue with template-based content? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    else:
        print(f"\n✅ Gemini will be used with model: {model_used}")
        
        # Update .env with working model if needed
        current_model = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        if model_used != current_model:
            print(f"  Updating .env to use {model_used}...")
            with open('.env', 'r') as f:
                lines = f.readlines()
            
            with open('.env', 'w') as f:
                for line in lines:
                    if line.startswith('MODEL_NAME='):
                        f.write(f'MODEL_NAME={model_used}\n')
                    else:
                        f.write(line)
            print(f"  ✅ Updated .env MODEL_NAME to {model_used}")
    
    # Verify output files
    verify_output_files()
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    
    print("\nTo ensure 100% LLM generation with Gemini:")
    print("1. Make sure GOOGLE_API_KEY is valid in .env file")
    print("2. Get a free API key from: https://makersuite.google.com/app/apikey")
    print("3. Current model: " + os.getenv("MODEL_NAME", "gemini-1.5-flash"))
    print("4. Run: python run.py")
    print("5. Execution should take 10-30 seconds for Gemini API calls")
    
    print("\nFree Gemini models available:")
    print("  • gemini-1.5-flash (fastest, free)")
    print("  • gemini-1.5-pro (more capable, free)")
    print("  • gemini-pro (legacy, free)")

if __name__ == "__main__":
    main()
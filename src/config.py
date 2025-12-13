import os
from langchain_google_genai import ChatGoogleGenerativeAI  # Changed from langchain_openai
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
import google.generativeai as genai  # Added for direct Gemini access

load_dotenv()


class Config:
    """Application configuration with Gemini LLM initialization"""
    
    def __init__(self):
        # Updated to use Google/Gemini API key
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment. Check your .env file")
        
        # Configure Gemini directly (for testing)
        genai.configure(api_key=self.google_api_key)
        
        # Get model from environment (you already have gemini-1.5-flash)
        self.model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        self.temperature = float(os.getenv("TEMPERATURE", "0.0"))
        
        # Initialize Gemini LLM via LangChain
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.google_api_key,
            max_output_tokens=2000,
            top_p=0.95,
            top_k=40
        )
        
        # JSON output parser for structured responses
        self.json_parser = JsonOutputParser()
    
    def get_llm_with_json_output(self):
        """Get LLM chain with JSON output parsing"""
        return self.llm | self.json_parser
    
    def test_llm_connection(self):
        """Test if Gemini connection works"""
        try:
            print(f"Testing Gemini API connection with {self.model_name}...")
            
            # Test via direct Gemini API first
            direct_model = genai.GenerativeModel(self.model_name)
            test_response = direct_model.generate_content(
                "Say 'Hello' in one word.",
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=10
                )
            )
            
            if test_response.text:
                print(f"✅ Direct Gemini connection successful using {self.model_name}")
                print(f"   Response: '{test_response.text}'")
                
                # Also test LangChain wrapper
                langchain_response = self.llm.invoke("Say 'OK' in one word.")
                if langchain_response.content:
                    print(f"✅ LangChain-Gemini integration successful")
                    return True
                else:
                    print("⚠️  Direct API works but LangChain wrapper failed")
                    return False
            return False
            
        except Exception as e:
            print(f"❌ Gemini connection failed: {e}")
            print("Trying alternative Gemini models...")
            
            # Try other Gemini models
            alternative_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
            
            for model in alternative_models:
                if model == self.model_name:
                    continue
                    
                try:
                    print(f"  Trying {model}...")
                    
                    # Update the LLM with alternative model
                    self.llm = ChatGoogleGenerativeAI(
                        model=model,
                        temperature=self.temperature,
                        google_api_key=self.google_api_key,
                        max_output_tokens=2000
                    )
                    
                    test_response = self.llm.invoke("Say 'Hello' in one word.")
                    if test_response.content:
                        print(f"✅ Gemini connection successful using {model} (fallback)")
                        self.model_name = model
                        return True
                except Exception as model_error:
                    print(f"    {model} failed: {str(model_error)[:50]}...")
            
            print("❌ All Gemini models failed. Please check:")
            print("   1. GOOGLE_API_KEY in .env file")
            print("   2. Internet connection")
            print("   3. Visit: https://makersuite.google.com/app/apikey")
            return False
    
    def get_direct_gemini_model(self):
        """Get direct Gemini model for advanced use cases"""
        return genai.GenerativeModel(self.model_name)
    
    def get_model_info(self):
        """Get information about the configured model"""
        return {
            "provider": "google",
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": 2000
        }
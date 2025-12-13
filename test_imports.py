#!/usr/bin/env python3
"""
Test all required imports for the Gemini-based system
"""

import sys

def test_import(module_name, import_path=None):
    """Test if a module can be imported"""
    try:
        if import_path:
            exec(f"from {module_name} import {import_path}")
        else:
            __import__(module_name)
        print(f"✅ {module_name}" + (f".{import_path}" if import_path else ""))
        return True
    except ImportError as e:
        print(f"❌ {module_name}" + (f".{import_path}" if import_path else ""))
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name}" + (f".{import_path}" if import_path else ""))
        print(f"   Warning: {e}")
        return True

print("Testing Gemini LangChain imports...")
print("="*50)

# Test core imports (Gemini version)
test_import("langchain")
test_import("langchain_google_genai")  # Changed from langchain_openai
test_import("langgraph")
test_import("pydantic")
test_import("google.generativeai")     # Changed from openai

# Test specific agent imports
print("\nTesting agent imports...")
print("-"*30)

import_attempts = [
    ("langchain.agents", "create_tool_calling_agent"),
    ("langchain.agents", "create_react_agent"),
    ("langchain.agents", "AgentExecutor"),
    ("langchain.agents", "initialize_agent"),
    ("langchain_core.prompts", "ChatPromptTemplate"),
    ("langchain_core.messages", "SystemMessage"),
    ("langchain_core.messages", "HumanMessage"),
    ("langchain_core.messages", "AIMessage"),
    ("langchain_core.output_parsers", "JsonOutputParser"),
]

for module, import_name in import_attempts:
    test_import(module, import_name)

# Test Gemini-specific imports
print("\nTesting Gemini-specific imports...")
print("-"*30)
gemini_imports = [
    ("langchain_google_genai", "ChatGoogleGenerativeAI"),
    ("google.generativeai", "configure"),
    ("google.generativeai", "GenerativeModel"),
    ("google.generativeai.types", "GenerationConfig"),
]

for module, import_name in gemini_imports:
    test_import(module, import_name)

# Test LangGraph imports
print("\nTesting LangGraph imports...")
print("-"*30)
langgraph_imports = [
    ("langgraph.graph", "StateGraph"),
    ("langgraph.graph", "END"),
    ("langgraph.prebuilt", "ToolExecutor"),
    ("langgraph.checkpoint", "MemorySaver"),
]

for module, import_name in langgraph_imports:
    test_import(module, import_name)

# Test our project imports
print("\nTesting project imports...")
print("-"*30)
try:
    from src.config import Config
    print("✅ src.config.Config")
    
    # Try to initialize config
    try:
        config = Config()
        print(f"   Config loaded: {config.model_name}")
    except Exception as e:
        print(f"⚠️  Config init: {e}")
    
except ImportError as e:
    print(f"❌ src.config.Config")
    print(f"   Error: {e}")

# Test agent imports
print("\nTesting agent class imports...")
print("-"*30)
agent_classes = [
    "DataProcessorAgent",
    "QuestionGeneratorAgent", 
    "ContentCreatorAgent",
    "ProductComparatorAgent",
]

for agent in agent_classes:
    try:
        exec(f"from src.agents.{agent.lower().replace('agent', '')} import {agent}")
        print(f"✅ {agent}")
    except ImportError as e:
        print(f"❌ {agent}")
        print(f"   Error: {e}")

print("\n" + "="*50)
print("Import test complete!")
print("\n📋 Summary:")
print("✅ Required for Gemini system:")
print("   • langchain")
print("   • langchain_google_genai (not langchain_openai)")
print("   • google.generativeai (not openai)")
print("   • langgraph")
print("   • pydantic")
print("   • python-dotenv")

print("\n🔧 If you see ❌ errors, run:")
print("pip install -r requirements.txt")
print("\n📁 Requirements.txt should contain:")
print("langchain>=0.1.0")
print("langchain-google-genai>=0.0.3")
print("langgraph>=0.0.26")
print("google-generativeai>=0.3.0")
print("pydantic>=2.5.0")
print("python-dotenv>=1.0.0")

print("\n🔑 Make sure .env file has:")
print("GOOGLE_API_KEY=your_actual_key_here")
print("MODEL_NAME=gemini-1.5-flash")
print("TEMPERATURE=0.0")
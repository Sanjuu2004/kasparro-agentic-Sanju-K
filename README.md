# Multi-Agent Content Generation System - Kasparro AI Engineer Challenge

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1%2B-orange.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.26%2B-purple.svg)
![Gemini](https://img.shields.io/badge/Google%20Gemini-API-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

*A production-ready agentic automation system powered by Google Gemini API*

</div>

## Overview

This is a **modular agentic automation system** designed for Kasparro's Applied AI Engineer Challenge. The system takes minimal product data and autonomously generates structured, machine-readable content pages through a sophisticated multi-agent workflow.

###  Key Features
- **Multi-Agent Architecture**: Specialized agents with clear responsibilities and boundaries
- **Google Gemini Integration**: Uses free-tier Google Gemini API for 100% LLM-driven content generation
- **LangGraph Orchestration**: Production-grade workflow management with state tracking
- **Modular Design**: Reusable content logic blocks and templates
- **Structured JSON Output**: Machine-readable outputs in clean JSON format
- **Production-Ready**: Error handling, fallback mechanisms, and comprehensive logging

## System Architecture

### Agent Roles & Responsibilities
| Agent | Responsibility | Output |
|-------|---------------|--------|
| **DataProcessorAgent** | Parses and validates raw product data into structured format | Validated `ProductData` model |
| **QuestionGeneratorAgent** | Generates 15+ categorized questions about the product | List of `GeneratedQuestion` objects |
| **ContentCreatorAgent** | Creates FAQ and product page content | `FAQItem` list and `ProductPage` structure |
| **ProductComparatorAgent** | Creates fictional products and generates comparisons | `ComparisonPage` with detailed analysis |

### Workflow Flowchart
```text
┌─────────────────┐
│ Raw Product     │
│     Data        │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Data Processor  │◄── Parse & Validate
└────────┬────────┘
         ▼
  ┌─────────────────────────────────────┐
  │      Parallel Agent Execution       │
  ├─────────────────┬───────────────────┤
  │                 │                   │
  ▼                 ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Question     │ │ Product Page │ │ Fictional    │
│ Generator    │ │ Generator    │ │ Product      │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                 │               │
       ▼                 │               │
┌──────────────┐         │               │
│ FAQ          │◄────────┘               │
│ Generator    │                         │
└──────┬───────┘                         │
       │                                 │
       └─────────────────┬───────────────┘
                         ▼
                ┌─────────────────┐
                │ Comparison      │
                │ Generator       │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │ JSON Output     │
                │ Compilation     │
                └─────────────────┘
```

## Quick Start
```text
### Prerequisites
- Python 3.11 or higher
- Google Gemini API key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))
- Git

### Installation
1. **Clone the repository**
   git clone https://github.com/yourusername/kasparro-ai-agentic-content-generation-system.git
   cd kasparro-ai-agentic-content-generation-system
Set up environment
# Install dependencies
pip install -r requirements.txt

# Set up environment (creates .env file)
python setup.py
Configure API key

Get your free API key from Google AI Studio

Edit .env file:

env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash
TEMPERATURE=0.0
Run the system

bash
# Verify setup
python verify_llm.py

# Run full system
python run.py

# Run individual agents (alternative)
python -m src.utils.main_agents
```
## Project Structure
```text
kasparro-ai-agentic-content-generation-system/
├── .env                          # Environment configuration
├── requirements.txt              # Python dependencies
├── run.py                        # Main entry point
├── verify_llm.py                 # Gemini API verification
├── setup.py                      # Project setup script
├── test_imports.py               # Dependency verification
├── outputs/                      # Generated JSON outputs
│   ├── faq.json
│   ├── product_page.json
│   └── comparison_page.json
├── docs/                         # Documentation
│   └── projectdocumentation.md
├── tests/                        # Test suite
│   ├── test_agents.py
│   └── test_logic_blocks.py
└── src/                          # Source code
    ├── config.py                 # Application configuration
    ├── main.py                   # System orchestration
    ├── core/                     # Core models and logic
    │   ├── models.py             # Data models (ProductData, FAQItem, etc.)
    │   ├── state.py              # State management
    │   ├── logic_blocks.py       # Reusable content logic blocks
    │   └── templates.py          # Content templates
    ├── agents/                   # Agent implementations
    │   ├── base_agent.py         # Base agent class
    │   ├── data_processor.py     # Data parsing agent
    │   ├── question_generator.py # Question generation agent
    │   ├── content_creator.py    # Content creation agent
    │   └── product_comparator.py # Comparison agent
    ├── orchestration/            # Workflow orchestration
    │   └── workflow.py           # LangGraph workflow
    └── utils/                    # Utility modules
        └── main_agents.py        # Alternative agent runner
```
## Configuration
**Environment Variables**
Create a .env file in the root directory:
```text
env
# Google Gemini Configuration (FREE TIER)
GOOGLE_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash
TEMPERATURE=0.0

# Optional Configuration
LOG_LEVEL=INFO
PREFERRED_PROVIDER=google
Input Data Format
The system accepts a JSON-like structure as input:

json
{
  "name": "GlowBoost Vitamin C Serum",
  "concentration": "10% Vitamin C",
  "skin_type": ["Oily", "Combination"],
  "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
  "benefits": ["Brightening", "Fades dark spots"],
  "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
  "side_effects": "Mild tingling for sensitive skin",
  "price": "₹699"
}
```
## Output Examples
**FAQ Output (faq.json)**
```text
json

{
  "product": "GlowBoost Vitamin C Serum",
  "faq_items": [
    {
      "question": "What is GlowBoost Vitamin C Serum?",
      "answer": "GlowBoost Vitamin C Serum is a 10% Vitamin C formulation designed for oily and combination skin types...",
      "category": "informational",
      "tags": ["basics", "introduction"]
    }
  ],
  "generated_at": "2024-01-15T10:30:00",
  "source": "google_gemini",
  "model": "gemini-2.0-flash"
}
```
**Product Page Output (product_page.json)**
```text

json
{
  "title": "GlowBoost Vitamin C Serum - Advanced Skincare Solution",
  "meta_description": "Professional 10% Vitamin C serum for oily and combination skin. Provides brightening and dark spot reduction.",
  "hero_section": {
    "headline": "Transform Your Skin with GlowBoost Vitamin C Serum",
    "subheadline": "Professional 10% Vitamin C serum for visible results"
  },
  "benefits_section": [
    {
      "benefit": "Brightening",
      "description": "Targets dullness by inhibiting melanin production",
      "scientific_basis": "Vitamin C inhibits tyrosinase enzyme"
    }
  ]
}
```
**Comparison Output (comparison_page.json)**
```text
json

{
  "title": "Comparison: GlowBoost Vitamin C Serum vs RadiantGlow Niacinamide Serum",
  "products": [
    {
      "name": "GlowBoost Vitamin C Serum",
      "type": "Vitamin C Serum",
      "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
      "best_for": "Oily, Combination skin",
      "price": "₹699",
      "rating": 4.5
    }
  ],
  "comparison_points": [
    {
      "aspect": "Active Ingredients",
      "product_a": "10% Vitamin C for brightening",
      "product_b": "5% Niacinamide for barrier repair",
      "winner": "Different focus",
      "explanation": "Different primary actives for different concerns"
    }
  ]
}
```
## 🧪 Testing & Verification
**Verify Setup**
```text
#Test all imports
python test_imports.py

#Verify Gemini API connection
python verify_llm.py

#Run unit tests
python -m pytest tests/
```
## Expected Output
When running python run.py, you should see:
```text
🚀 Starting content generation workflow with Google Gemini...
   Model: gemini-2.0-flash
   Using: LangGraph workflow

✅ Parsed: GlowBoost Vitamin C Serum
✅ Generated 15 questions using Gemini
✅ Created fictional product: RadiantGlow Niacinamide Serum
✅ Generated 5 FAQ items using Gemini
✅ Generated product page using Gemini
✅ Generated comparison using Gemini
✅ Saved 3 output files

🎉 Content Generation Complete with Gemini!
✅ 100% LLM-generated content verified
```
## Troubleshooting
**Common Issues**
```text
**"404 model not found" error**

Update .env to use latest Gemini models: gemini-2.0-flash or gemini-2.5-flash-lite

Run: python verify_llm.py to test connection

**"429 quota exceeded" error**

Ensure billing is enabled in Google Cloud Console

Request Tier 1 upgrade via Google AI Developers Forum

Use gemini-2.5-flash-lite as temporary alternative

**Import errors**

Install all dependencies: pip install -r requirements.txt

Check Python version: python --version (requires 3.11+)

**No output files generated**

Check outputs/ directory permissions

Verify .env file has correct API key

Run with verbose logging: LOG_LEVEL=DEBUG python run.py
```
## Debug Mode
Enable detailed logging for troubleshooting:
```text
export LOG_LEVEL=DEBUG
python run.py
```
## Performance & Optimization
**Execution Time**

First run: 20-30 seconds (includes API warm-up)

Subsequent runs: 10-15 seconds (cached connections)

Without LLM calls: < 2 seconds (fallback templates)
**
Token Usage**
Average per run: 3,000-5,000 tokens

Cost (free tier): $0.00/month (Gemini free tier)

Cost (paid tier): ~$0.01-$0.02 per run

**Optimization Tips**
Batch processing: Process multiple products in sequence

Template caching: Cache frequently used templates

Connection pooling: Reuse Gemini API connections

Fallback strategies: Use template content when API fails

## Extending the System
Adding New Agents
Create agent class in src/agents/

Inherit from BaseAgent

Implement required methods

Register in workflow

Adding Content Types
Add template in core/templates.py

Create logic blocks in core/logic_blocks.py

Update output schema in core/models.py

Create new agent or extend existing ones

Integrating Other LLMs
The system supports multiple LLM providers:

Update src/config.py for new provider

Implement provider-specific agent adapters

Update .env configuration

## Documentation
**API Documentation**
Google Gemini API: https://ai.google.dev/gemini-api

LangChain Documentation: https://python.langchain.com

LangGraph Documentation: https://langchain-ai.github.io/langgraph

Project Documentation
Full system design: docs/projectdocumentation.md

Agent specifications: docs/agents.md

API reference: docs/api.md

## Contributing
```text
1.Fork the repository
2.Create feature branch: git checkout -b feature/new-agent
3.Commit changes: git commit -am 'Add new agent'
4.Push to branch: git push origin feature/new-agent
5.Submit pull request
```
**Development Setup**
```text
# Clone repository
git clone https://github.com/yourusername/kasparro-ai-agentic-content-generation-system.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

# Multi-Agent Content Generation System

## Overview
A production-grade multi-agent system for automated content generation from product data. Built for the Kasparro Applied AI Engineer challenge.

## Features
- **Multi-Agent Architecture**: 7 specialized agents with clear boundaries
- **DAG Orchestration**: Automated dependency management and execution
- **Reusable Logic Blocks**: Modular content transformation components
- **Template Engine**: Structured content generation with validation
- **State Management**: Immutable state with message passing
- **JSON Output**: Machine-readable structured content pages

## System Architecture
```text
 Input Data → Agents → Logic Blocks → Templates → JSON Output
 ```
 
### Agents
1. **Data Ingestion Agent**: Parses and validates input data
2. **Question Generation Agent**: Creates 15+ categorized user questions
3. **Product B Creation Agent**: Generates fictional product for comparison
4. **FAQ Generation Agent**: Creates FAQ page with Q&As
5. **Product Page Agent**: Generates detailed product description
6. **Comparison Page Agent**: Creates product comparison matrix
7. **Output Generation Agent**: Writes JSON files to disk

## Installation
```bash
# Clone repository
git clone https://github.com/yourusername/kasparro-ai-agentic-content-generation-system-sanju-k.git

# Install dependencies
cd kasparro-ai-agentic-content-generation-system-sanju-k
pip install -e .

# Set up environment
cp .env.example .env
# Add your OpenAI API key to .env

**Usage**
 ```text
 # Run the system
python src/main.py

# Run tests
pytest tests/

# View generated content
ls outputs/
# faq.json, product_page.json, comparison_page.json
```
**Output Structure**
```text
outputs/
├── faq.json                    # FAQ page with structured data
├── product_page.json          # Complete product page
└── comparison_page.json       # Product comparison matrix

docs/
├── projectdocumentation.md    # System documentation
├── execution_report.json      # Pipeline execution report
└── diagrams/
    └── execution_dag.png      # DAG visualization
```
**System Requirements**
Python 3.11+

OpenAI API key (for potential future LLM integration)

100MB disk space

**Design Principles**

1.Single Responsibility: Each agent does one thing well

2.Immutability: State updates create new objects

3.Composability: Logic blocks and templates are reusable

4.Extensibility: Easy to add new agents or content types

5.Observability: Full execution tracking and logging.

**Extending the System**

**Add a New Logic Block**
```text
from src.core.logic_blocks import LogicBlock, ContentBlockType

class NewLogicBlock(LogicBlock):
    def __init__(self):
        super().__init__(ContentBlockType.NEW_BLOCK)
    
    def execute(self, product_data, context):
        # Your transformation logic
        return transformed_data

# Register in factory
LogicBlockFactory.register_block(ContentBlockType.NEW_BLOCK, NewLogicBlock)
```
**Add a New Agent**
```text
from src.agents.base import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__("new_agent_id", "New Agent Name")
    
    async def _execute_impl(self, context):
        # Your agent logic
        return result_data
```
**Testing**
```text
# Run all tests
pytest

# Run specific test
pytest tests/test_logic_blocks.py -v

# Run with coverage
pytest --cov=src tests/
```
**Author**
Sanju - Kasparro Applied AI Engineer Challenge
```text

This implementation provides:

## Unique Features:

1. **True Multi-Agent Architecture**: Each agent has clear boundaries, single responsibility, and communicates via structured messages.

2. **DAG-Based Orchestration**: Visual pipeline with dependency management and parallel execution potential.

3. **Reusable Logic Blocks**: Production-ready content transformation modules with scientific backing.

4. **Custom Template Engine**: Not just prompting - a real template system with validation, transformation, and computed fields.

5. **Immutable State Management**: Thread-safe state updates with history tracking.

6. **Visualization**: Automatic DAG graph generation for system understanding.

7. **Error Isolation**: Each agent's failures don't crash the entire pipeline.

8. **Extensibility Points**: Easy to add new agents, logic blocks, or templates.

## To Run:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the system
python src/main.py

# Check outputs
ls outputs/
# Should see: faq.json, product_page.json, comparison_page.json

# View documentation
open docs/projectdocumentation.md
```
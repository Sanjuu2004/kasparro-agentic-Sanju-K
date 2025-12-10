# Multi-Agent Content Generation System

## Problem Statement
Design and implement a modular agentic automation system that takes a small product dataset and automatically generates structured, machine-readable content pages. The system must demonstrate production-quality engineering with clear agent boundaries, reusable components, and an orchestration graph.

## Solution Overview
The system implements a directed acyclic graph (DAG) of specialized agents that process product data through a pipeline. Each agent has a single responsibility and communicates through a shared state manager. The system generates three types of content pages (FAQ, Product Description, Comparison) using reusable logic blocks and template-based generation.

## Scopes & Assumptions

### In Scope
- Multi-agent orchestration with dependency management
- Reusable content logic blocks for transformation
- Template-based content generation
- Structured JSON output
- Error handling and state management
- Execution visualization and reporting

### Out of Scope
- External API calls or research
- Adding new facts beyond provided data
- UI/website implementation
- User authentication
- Database persistence

### Assumptions
- Product data is consistent and properly formatted
- All required information is present in input data
- System runs in a controlled environment
- Python 3.11+ is available

## System Design

### Architecture Overview
The system follows a pipeline architecture with these components:

1. **State Manager**: Central state container with immutability
2. **Logic Blocks**: Reusable content transformation modules
3. **Agents**: Specialized workers with single responsibilities
4. **Templates**: Structured content definitions with field rules
5. **Orchestrator**: DAG-based execution coordinator

### Agent Design Pattern
Each agent implements:
- Single responsibility principle
- Defined input/output contracts
- Dependency declaration
- Error handling and logging
- State communication via messages

### Content Generation Pipeline
```text
Raw Data → [Ingestion Agent] → Product Data
↓
[Question Generation Agent] → User Questions
↓
[Logic Block Execution] → Content Blocks
↓
[Template Application] → Structured Content
↓
[Output Agent] → JSON Files
```
### DAG Execution Flow
graph TD
    A[data_ingestion] --> B[question_generation]
    A --> C[product_b_creation]
    B --> D[faq_generation]
    C --> E[comparison_page_agent]
    A --> F[product_page_agent]
    D --> G[output_generation_agent]
    E --> G
    F --> G
    
### Key Design Decisions

1. **Immutable State**: State updates create new objects to prevent side effects
2. **Template Engine**: Custom template system with field validation and transformation
3. **Logic Block Registry**: Factory pattern for reusable content transformations
4. **Agent Messaging**: Structured communication between agents via state
5. **DAG Visualization**: Automatic generation of execution graphs

### Error Handling Strategy
- Individual agent error isolation
- State-based error logging
- Dependency validation before execution
- Graceful pipeline termination

### Extensibility Points
1. Add new logic blocks by extending `LogicBlock` class
2. Register new templates in `TemplateFactory`
3. Add new agents by extending `BaseAgent`
4. Modify DAG dependencies in orchestrator

## Data Flow
1. **Input**: Raw product JSON data
2. **Processing**: Through 7 specialized agents
3. **Transformation**: Via 4+ logic blocks
4. **Templating**: Through 3 content templates
5. **Output**: 3 structured JSON files

## Performance Considerations
- Async execution for I/O bound operations
- Caching of logic block results
- Efficient state updates
- Parallel execution where possible

## Testing Strategy
- Unit tests for logic blocks
- Integration tests for agent pipelines
- Template validation tests
- State management tests

## Deployment Considerations
- Environment variable configuration
- Logging configuration
- Monitoring via agent messages
- Output validation

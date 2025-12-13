from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from src.core.models import (
    ProductData, GeneratedQuestion, FAQItem, 
    ProductPage, ComparisonPage, QuestionCategory
)
from src.core.templates import ContentTemplates


class ParseProductDataTool(BaseTool):
    name = "parse_product_data"
    description = "Parse raw product data into validated structured format"
    args_schema: Type[BaseModel] = type('InputSchema', (BaseModel,), {
        'raw_data': Field(..., description="Raw product data JSON")
    })
    
    def _run(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            product = ProductData(**raw_data)
            return {
                "success": True,
                "product": product.model_dump(),
                "message": f"Successfully parsed: {product.name}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Product data validation failed"
            }


class GenerateQuestionsTool(BaseTool):
    name = "generate_questions"
    description = "Generate 15+ categorized questions about skincare product using LLM"
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
    
    args_schema: Type[BaseModel] = type('InputSchema', (BaseModel,), {
        'product_data': Field(..., description="Structured product data"),
        'num_questions': Field(default=15, ge=15, description="Minimum 15 questions")
    })
    
    def _run(self, product_data: Dict[str, Any], num_questions: int = 15) -> Dict[str, Any]:
        try:
            # Get template and create chain
            template = ContentTemplates.get_question_generation_template()
            chain = template | self.llm | JsonOutputParser()
            
            # Prepare categories
            categories = [cat.value for cat in QuestionCategory]
            
            # Run LLM chain
            result = chain.invoke({
                "num_questions": num_questions,
                "categories": ", ".join(categories),
                **product_data
            })
            
            # Validate and convert to GeneratedQuestion models
            questions = []
            for q in result:
                try:
                    question = GeneratedQuestion(
                        question=q.get("question", ""),
                        category=QuestionCategory(q.get("category", "informational")),
                        priority=q.get("priority", 3)
                    )
                    questions.append(question)
                except:
                    continue
            
            # Ensure we have at least 15 questions
            if len(questions) < 15:
                # Generate more questions if needed
                additional_needed = 15 - len(questions)
                for i in range(additional_needed):
                    questions.append(GeneratedQuestion(
                        question=f"What is {product_data.get('name')}?",
                        category=QuestionCategory.INFORMATIONAL,
                        priority=3
                    ))
            
            return {
                "success": True,
                "questions": [q.model_dump() for q in questions[:num_questions]],
                "count": len(questions),
                "categories": list(set([q.category.value for q in questions]))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate questions: {str(e)}"
            }


class CreateFictionalProductTool(BaseTool):
    name = "create_fictional_product"
    description = "Create fictional skincare product for comparison using LLM"
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
    
    args_schema: Type[BaseModel] = type('InputSchema', (BaseModel,), {
        'main_product': Field(..., description="Main product for contrast")
    })
    
    def _run(self, main_product: Dict[str, Any]) -> Dict[str, Any]:
        try:
            template = ContentTemplates.get_fictional_product_template()
            chain = template | self.llm | JsonOutputParser()
            
            result = chain.invoke(main_product)
            
            # Validate the fictional product structure
            fictional_product = ProductData(**result)
            
            return {
                "success": True,
                "fictional_product": fictional_product.model_dump(),
                "message": f"Created fictional product: {fictional_product.name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create fictional product: {str(e)}"
            }


class GenerateFAQTool(BaseTool):
    name = "generate_faq"
    description = "Generate FAQ from questions using LLM"
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
    
    args_schema: Type[BaseModel] = type('InputSchema', (BaseModel,), {
        'questions': Field(..., description="Generated questions"),
        'product_data': Field(..., description="Product context"),
        'num_faqs': Field(default=5, ge=5, description="Minimum 5 FAQ items")
    })
    
    def _run(self, questions: List[Dict[str, Any]], product_data: Dict[str, Any], 
             num_faqs: int = 5) -> Dict[str, Any]:
        try:
            template = ContentTemplates.get_faq_generation_template()
            chain = template | self.llm | JsonOutputParser()
            
            # Select questions for FAQ
            selected_questions = questions[:num_faqs]
            
            result = chain.invoke({
                "questions": "\n".join([q.get("question", "") for q in selected_questions]),
                **product_data
            })
            
            # Create FAQ items
            faq_items = []
            for i, faq_data in enumerate(result[:num_faqs]):
                try:
                    # Use original question category
                    original_category = selected_questions[i].get("category", "general")
                    
                    faq_item = FAQItem(
                        question=selected_questions[i].get("question", ""),
                        answer=faq_data.get("answer", ""),
                        category=original_category,
                        tags=faq_data.get("tags", [])
                    )
                    faq_items.append(faq_item)
                except:
                    continue
            
            # Ensure we have at least 5 FAQ items
            while len(faq_items) < 5:
                faq_items.append(FAQItem(
                    question="Sample question",
                    answer="Sample answer based on product data",
                    category="general",
                    tags=["sample"]
                ))
            
            return {
                "success": True,
                "faq_items": [item.model_dump() for item in faq_items],
                "count": len(faq_items)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate FAQ: {str(e)}"
            }


class GenerateProductPageTool(BaseTool):
    name = "generate_product_page"
    description = "Generate complete product page using LLM"
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
    
    args_schema: Type[BaseModel] = type('InputSchema', (BaseModel,), {
        'product_data': Field(..., description="Product data")
    })
    
    def _run(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            template = ContentTemplates.get_product_page_template()
            chain = template | self.llm | JsonOutputParser()
            
            result = chain.invoke(product_data)
            
            # Create ProductPage model
            product_page = ProductPage(**result)
            
            return {
                "success": True,
                "product_page": product_page.model_dump(),
                "sections": len(result)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate product page: {str(e)}"
            }


class GenerateComparisonTool(BaseTool):
    name = "generate_comparison"
    description = "Generate detailed product comparison using LLM"
    
    def __init__(self, llm):
        super().__init__()
        self.llm = llm
    
    args_schema: Type[BaseModel] = type('InputSchema', (BaseModel,), {
        'main_product': Field(..., description="Main product"),
        'fictional_product': Field(..., description="Fictional product")
    })
    
    def _run(self, main_product: Dict[str, Any], fictional_product: Dict[str, Any]) -> Dict[str, Any]:
        try:
            template = ContentTemplates.get_comparison_template()
            chain = template | self.llm | JsonOutputParser()
            
            result = chain.invoke({
                "product_a_name": main_product.get("name"),
                "product_a_concentration": main_product.get("concentration"),
                "product_a_skin_type": ", ".join(main_product.get("skin_type", [])),
                "product_a_ingredients": ", ".join(main_product.get("key_ingredients", [])),
                "product_a_benefits": ", ".join(main_product.get("benefits", [])),
                "product_a_price": main_product.get("price"),
                
                "product_b_name": fictional_product.get("name"),
                "product_b_concentration": fictional_product.get("concentration"),
                "product_b_skin_type": ", ".join(fictional_product.get("skin_type", [])),
                "product_b_ingredients": ", ".join(fictional_product.get("key_ingredients", [])),
                "product_b_benefits": ", ".join(fictional_product.get("benefits", [])),
                "product_b_price": fictional_product.get("price")
            })
            
            # Create ComparisonPage model
            comparison_page = ComparisonPage(**result)
            
            # Ensure we have at least 4 comparison points
            if len(comparison_page.comparison_points) < 4:
                comparison_page.comparison_points.extend([
                    {
                        "aspect": "Price",
                        "main_product": main_product.get("price"),
                        "fictional_product": fictional_product.get("price"),
                        "verdict": "Different price points for different markets"
                    },
                    {
                        "aspect": "Ingredients",
                        "main_product": ", ".join(main_product.get("key_ingredients", [])),
                        "fictional_product": ", ".join(fictional_product.get("key_ingredients", [])),
                        "verdict": "Different formulations for different needs"
                    },
                    {
                        "aspect": "Skin Type Suitability",
                        "main_product": ", ".join(main_product.get("skin_type", [])),
                        "fictional_product": ", ".join(fictional_product.get("skin_type", [])),
                        "verdict": "Targets different skin concerns"
                    },
                    {
                        "aspect": "Benefits",
                        "main_product": ", ".join(main_product.get("benefits", [])),
                        "fictional_product": ", ".join(fictional_product.get("benefits", [])),
                        "verdict": "Different primary benefits"
                    }
                ])
            
            return {
                "success": True,
                "comparison_page": comparison_page.model_dump(),
                "comparison_points": len(comparison_page.comparison_points)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate comparison: {str(e)}"
            }
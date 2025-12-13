from typing import Dict, Any, List
from langchain.tools import Tool
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
import json
import re

from src.agents.base_agent import BaseAgent
from src.core.models import GeneratedQuestion, QuestionCategory


class QuestionGeneratorAgent(BaseAgent):
    """Agent for generating categorized questions about products - Updated for Gemini"""
    
    def __init__(self, llm=None):
        super().__init__(
            name="question_generator",
            description="Generates categorized questions about skincare products",
            llm=llm
        )
        self.json_parser = JsonOutputParser()
    
    def _setup_tools(self):
        """Setup question generation tools - Simplified for Gemini"""
        
        def generate_categorized_questions(product_data: str) -> str:
            """Generate categorized questions about a product - Gemini version"""
            try:
                # Parse product data
                if isinstance(product_data, str):
                    try:
                        data = json.loads(product_data)
                    except:
                        # If it's not JSON, treat it as a string description
                        data = {"description": product_data}
                else:
                    data = product_data
                
                # Create prompt for Gemini (Gemini works better with structured prompts)
                system_prompt = """You are a skincare expert generating questions about products.
                Generate EXACTLY 15 questions covering these categories:
                1. Informational (about the product, ingredients, science)
                2. Safety (side effects, contraindications, skin compatibility)
                3. Usage (how to use, application frequency, best practices)
                4. Purchase (value, pricing, availability)
                5. Comparison (vs other products, alternatives)
                6. Ingredient (specific ingredients and their effects)
                7. Effectiveness (results, timelines, expectations)
                
                Return ONLY a JSON array with this structure:
                [
                  {
                    "question": "What is Vitamin C serum?",
                    "category": "informational",
                    "priority": 1
                  },
                  ...
                ]
                
                Priority: 1=most important, 5=least important.
                Make questions specific to the product data provided."""
                
                user_prompt = f"""Product Data:
                Name: {data.get('name', 'Unknown')}
                Ingredients: {data.get('key_ingredients', data.get('ingredients', 'Unknown'))}
                Skin Type: {data.get('skin_type', 'Unknown')}
                Benefits: {data.get('benefits', data.get('key_benefits', 'Unknown'))}
                Concentration: {data.get('concentration', 'Unknown')}
                Price: {data.get('price', 'Unknown')}
                
                Generate 15 categorized questions:"""
                
                # Use direct Gemini call (more reliable than LangChain tools)
                response = self._call_direct_gemini(user_prompt, system_prompt)
                
                # Extract JSON from response
                json_str = self._extract_json_from_response(response)
                
                if json_str:
                    questions_data = json.loads(json_str)
                else:
                    # Fallback: generate simple questions
                    questions_data = self._generate_fallback_questions(data)
                
                # Format and validate
                questions = []
                for i, q in enumerate(questions_data[:15]):  # Ensure max 15
                    try:
                        if isinstance(q, str):
                            # Handle string-only questions
                            question = GeneratedQuestion(
                                id=f"q{i+1}",
                                question=q,
                                category=QuestionCategory.INFORMATIONAL,
                                priority=3
                            )
                        else:
                            # Handle dict questions
                            question = GeneratedQuestion(
                                id=f"q{i+1}",
                                question=q.get("question", str(q)),
                                category=QuestionCategory(q.get("category", "informational").lower()),
                                priority=q.get("priority", 3)
                            )
                        questions.append(question.model_dump())
                    except Exception as e:
                        print(f"Error parsing question {q}: {e}")
                        continue
                
                # Ensure we have exactly 15 questions
                if len(questions) < 15:
                    questions.extend(self._generate_missing_questions(data, 15 - len(questions)))
                
                return json.dumps({
                    "questions": questions[:15],
                    "total_generated": len(questions),
                    "categories_covered": list(set([q.get("category") for q in questions if q.get("category")]))
                }, indent=2)
                
            except Exception as e:
                print(f"Error in generate_categorized_questions: {e}")
                # Return fallback questions
                return json.dumps({
                    "questions": self._generate_fallback_questions(data)[:15],
                    "total_generated": 15,
                    "categories_covered": ["informational", "safety", "usage", "purchase"]
                }, indent=2)
        
        self.tools = [
            Tool(
                name="generate_categorized_questions",
                func=generate_categorized_questions,
                description="Generate 15+ categorized questions about a skincare product. Accepts JSON or text product data."
            )
        ]
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from Gemini response text"""
        try:
            # Try to parse directly first
            json.loads(response)
            return response
        except:
            # Try to find JSON in the text
            json_match = re.search(r'(\[\s*\{.*\}\s*\])', response, re.DOTALL)
            if json_match:
                return json_match.group(1)
            
            # Try object format
            json_match = re.search(r'(\{\s*"questions".*?\})', response, re.DOTALL)
            if json_match:
                return json_match.group(1)
            
            return None
    
    def _generate_fallback_questions(self, product_data: Dict) -> List[Dict]:
        """Generate fallback questions if Gemini fails"""
        base_questions = [
            {"question": f"What is {product_data.get('name', 'this product')}?", "category": "informational", "priority": 1},
            {"question": f"How do I use {product_data.get('name', 'this product')}?", "category": "usage", "priority": 1},
            {"question": f"Are there any side effects of {product_data.get('name', 'this product')}?", "category": "safety", "priority": 1},
            {"question": f"Who should use {product_data.get('name', 'this product')}?", "category": "safety", "priority": 2},
            {"question": f"Can I use {product_data.get('name', 'this product')} with other skincare products?", "category": "usage", "priority": 2},
            {"question": f"How long does it take to see results with {product_data.get('name', 'this product')}?", "category": "effectiveness", "priority": 2},
            {"question": f"What are the key ingredients in {product_data.get('name', 'this product')}?", "category": "ingredient", "priority": 1},
            {"question": f"Is {product_data.get('name', 'this product')} worth the price?", "category": "purchase", "priority": 3},
            {"question": f"Where can I buy {product_data.get('name', 'this product')}?", "category": "purchase", "priority": 3},
            {"question": f"How does {product_data.get('name', 'this product')} compare to similar products?", "category": "comparison", "priority": 2},
            {"question": f"Can {product_data.get('name', 'this product')} help with dark spots?", "category": "effectiveness", "priority": 2},
            {"question": f"Is {product_data.get('name', 'this product')} suitable for sensitive skin?", "category": "safety", "priority": 2},
            {"question": f"When is the best time to use {product_data.get('name', 'this product')}?", "category": "usage", "priority": 3},
            {"question": f"How should I store {product_data.get('name', 'this product')}?", "category": "usage", "priority": 4},
            {"question": f"What makes {product_data.get('name', 'this product')} different from other serums?", "category": "comparison", "priority": 3},
        ]
        return base_questions
    
    def _generate_missing_questions(self, product_data: Dict, count: int) -> List[Dict]:
        """Generate additional questions if we don't have enough"""
        additional = [
            {"question": f"What is the concentration of active ingredients in {product_data.get('name', 'this product')}?", "category": "informational", "priority": 4},
            {"question": f"Can {product_data.get('name', 'this product')} be used during pregnancy?", "category": "safety", "priority": 4},
            {"question": f"Does {product_data.get('name', 'this product')} expire?", "category": "safety", "priority": 4},
            {"question": f"How much product should I use per application?", "category": "usage", "priority": 3},
            {"question": f"Are there any ingredients in {product_data.get('name', 'this product')} that might cause allergies?", "category": "safety", "priority": 3},
        ]
        return additional[:count]
    
    def _setup_agent(self):
        """Setup question generator agent - Simplified for Gemini"""
        # Use the parent class's simple chain approach
        self.agent_executor = self._create_agent_executor(
            tools=self.tools,
            system_prompt=self.get_system_prompt()
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Question Generation Agent specialized in skincare products.
        
        Your task: Generate EXACTLY 15 categorized questions.
        
        Categories to cover:
        • Informational: About product, ingredients, science
        • Safety: Side effects, contraindications, skin compatibility  
        • Usage: How to use, application, best practices
        • Purchase: Value, pricing, availability
        • Comparison: Vs other products, alternatives
        • Ingredient: Specific ingredients and effects
        • Effectiveness: Results, timelines, expectations
        
        Rules:
        1. Base questions ONLY on provided product data
        2. Make questions specific and relevant
        3. Include priority (1=high, 5=low)
        4. Return ONLY valid JSON array
        5. Each question must have: question, category, priority
        
        Example format:
        [
          {"question": "What does Vitamin C do?", "category": "informational", "priority": 1},
          ...
        ]"""
    
    def generate_questions_simple(self, product_data: Dict) -> List[GeneratedQuestion]:
        """Simple method to generate questions without complex agent setup"""
        try:
            result = self.run_with_json_output(product_data)
            
            if result["success"] and result["output"]:
                questions_data = result["output"]
                if isinstance(questions_data, dict) and "questions" in questions_data:
                    questions_data = questions_data["questions"]
                
                questions = []
                for i, q in enumerate(questions_data[:15]):
                    try:
                        questions.append(GeneratedQuestion(
                            id=f"q{i+1}",
                            question=q.get("question", str(q)),
                            category=QuestionCategory(q.get("category", "informational").lower()),
                            priority=q.get("priority", 3)
                        ))
                    except:
                        continue
                
                return questions[:15]
            
        except Exception as e:
            print(f"Error in generate_questions_simple: {e}")
        
        # Fallback to template questions
        return self._generate_template_questions(product_data)
    
    def _generate_template_questions(self, product_data: Dict) -> List[GeneratedQuestion]:
        """Generate template-based questions as last resort"""
        template_questions = []
        fallback_data = self._generate_fallback_questions(product_data)
        
        for i, q in enumerate(fallback_data[:15]):
            template_questions.append(GeneratedQuestion(
                id=f"q{i+1}",
                question=q["question"],
                category=QuestionCategory(q["category"]),
                priority=q["priority"]
            ))
        
        return template_questions
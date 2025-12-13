from typing import Dict, Any, List
from langchain.tools import Tool
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
import json
import re

from src.agents.base_agent import BaseAgent
from src.core.models import FAQItem, ProductPage


class ContentCreatorAgent(BaseAgent):
    """Agent for creating various content types (FAQ, Product Page) - Updated for Gemini"""
    
    def __init__(self, llm=None):
        super().__init__(
            name="content_creator",
            description="Creates FAQ and product page content",
            llm=llm
        )
        self.json_parser = JsonOutputParser()
    
    def _setup_tools(self):
        """Setup content creation tools - Simplified for Gemini"""
        
        def generate_faq_content(input_data: str) -> str:
            """Generate FAQ content from questions and product data - Gemini version"""
            try:
                # Parse input
                if isinstance(input_data, str):
                    try:
                        data = json.loads(input_data)
                    except:
                        # Handle plain text input
                        data = {"questions": [], "description": input_data}
                else:
                    data = input_data
                
                questions = data.get("questions", [])
                product_data = data.get("product_data", {})
                
                # If no product_data provided, use the whole data as product info
                if not product_data:
                    product_data = data
                
                # Create FAQ using direct Gemini call
                system_prompt = """You are a skincare content expert creating FAQ sections.
                
                Your task: Create detailed, helpful answers for skincare product questions.
                
                Format each FAQ item as:
                {
                  "question": "The original question",
                  "answer": "Detailed, helpful answer (3-5 sentences)",
                  "category": "question category",
                  "tags": ["relevant", "tags"]
                }
                
                Guidelines:
                1. Answers must be based ONLY on provided product data
                2. Keep answers professional and factual
                3. Include key ingredients, benefits, usage instructions
                4. Address safety concerns honestly
                5. Add relevant tags like "ingredients", "safety", "usage", etc.
                
                Return ONLY a JSON array of FAQ items."""
                
                # Prepare questions text
                if questions:
                    if isinstance(questions[0], dict):
                        questions_text = "\n".join([f"{i+1}. {q.get('question', '')} (Category: {q.get('category', 'general')})" 
                                                   for i, q in enumerate(questions[:5])])
                    else:
                        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions[:5])])
                else:
                    # Generate default questions if none provided
                    questions_text = """1. What is this product and what does it do?
2. How do I use this product?
3. Are there any side effects or precautions?
4. Who should use this product?
5. How long does it take to see results?"""
                
                user_prompt = f"""Product Information:
                Name: {product_data.get('name', 'Skincare Product')}
                Ingredients: {product_data.get('key_ingredients', product_data.get('ingredients', 'Not specified'))}
                Benefits: {product_data.get('benefits', product_data.get('key_benefits', 'Not specified'))}
                Skin Type: {product_data.get('skin_type', 'Various')}
                Price: {product_data.get('price', 'Not specified')}
                Usage: {product_data.get('how_to_use', product_data.get('usage', 'Not specified'))}
                Side Effects: {product_data.get('side_effects', product_data.get('safety', 'None known'))}
                
                Questions to Answer:
                {questions_text}
                
                Create detailed answers for these questions:"""
                
                # Use direct Gemini call
                response = self._call_direct_gemini(user_prompt, system_prompt)
                
                # Extract JSON from response
                json_str = self._extract_json_from_response(response)
                
                if json_str:
                    try:
                        faq_data = json.loads(json_str)
                    except:
                        faq_data = []
                else:
                    # Generate fallback FAQ
                    faq_data = self._generate_fallback_faq(questions, product_data)
                
                # Create FAQ items
                faq_items = []
                for i, item in enumerate(faq_data[:5]):  # Max 5 items as required
                    try:
                        if isinstance(item, dict):
                            question = item.get("question", "")
                            answer = item.get("answer", "")
                            category = item.get("category", "general")
                            tags = item.get("tags", [])
                        else:
                            # Handle string or unexpected format
                            question = questions[i].get("question", f"Question {i+1}") if i < len(questions) else f"Question {i+1}"
                            answer = str(item)
                            category = "general"
                            tags = []
                        
                        # Create FAQItem
                        faq_item = FAQItem(
                            question=question,
                            answer=answer,
                            category=category,
                            tags=tags
                        )
                        faq_items.append(faq_item.model_dump())
                    except Exception as e:
                        print(f"Error processing FAQ item {i}: {e}")
                        continue
                
                # Ensure at least 5 FAQ items
                if len(faq_items) < 5:
                    faq_items.extend(self._generate_missing_faq_items(product_data, 5 - len(faq_items)))
                
                return json.dumps({
                    "faq_items": faq_items[:5],
                    "total_items": len(faq_items),
                    "status": "success"
                }, indent=2)
                
            except Exception as e:
                print(f"Error generating FAQ: {e}")
                return json.dumps({
                    "faq_items": self._generate_fallback_faq([], product_data)[:5],
                    "total_items": 5,
                    "status": "fallback",
                    "error": str(e)
                }, indent=2)
        
        def generate_product_page(product_data: str) -> str:
            """Generate complete product page - Gemini version"""
            try:
                # Parse product data
                if isinstance(product_data, str):
                    try:
                        data = json.loads(product_data)
                    except:
                        data = {"description": product_data}
                else:
                    data = product_data
                
                # Create system prompt for product page
                system_prompt = """You are a professional skincare copywriter creating product pages.
                
                Create a complete, compelling product page with these sections:
                1. Hero Section: Title, tagline, key selling points
                2. Benefits Section: Detailed benefits with scientific backing
                3. Ingredients Section: Key ingredients explained
                4. Usage Section: How to use, frequency, best practices
                5. Safety Section: Side effects, precautions, who should avoid
                6. Pricing Section: Price, value proposition
                7. CTA Section: Call to action buttons/messages
                
                Return ONLY valid JSON in this exact structure:
                {
                  "title": "Product Name",
                  "meta_description": "SEO-friendly description",
                  "hero_section": {
                    "headline": "Main headline",
                    "subheadline": "Supporting text",
                    "key_points": ["Point 1", "Point 2", "Point 3"]
                  },
                  "benefits_section": [
                    {
                      "benefit": "Brightening",
                      "description": "How it brightens",
                      "scientific_basis": "Scientific explanation"
                    }
                  ],
                  "ingredients_section": [
                    {
                      "ingredient": "Vitamin C",
                      "purpose": "Antioxidant protection",
                      "benefits": ["Brightening", "Collagen production"]
                    }
                  ],
                  "usage_section": {
                    "instructions": "Step-by-step instructions",
                    "frequency": "How often to use",
                    "best_practices": ["Tip 1", "Tip 2"]
                  },
                  "safety_section": {
                    "side_effects": "Possible side effects",
                    "precautions": "Who should be careful",
                    "contraindications": "When not to use"
                  },
                  "pricing_section": {
                    "price": "$XX.XX",
                    "value_proposition": "Why it's worth it",
                    "comparison_value": "Vs alternatives"
                  },
                  "cta_section": {
                    "primary_cta": "Buy Now",
                    "secondary_cta": "Learn More",
                    "urgency_message": "Limited time offer"
                  }
                }"""
                
                user_prompt = f"""Create a product page for this skincare product:
                
                Product Name: {data.get('name', 'GlowBoost Vitamin C Serum')}
                Concentration: {data.get('concentration', '10% Vitamin C')}
                Skin Type: {data.get('skin_type', 'Oily, Combination')}
                Key Ingredients: {data.get('key_ingredients', data.get('ingredients', ['Vitamin C', 'Hyaluronic Acid']))}
                Benefits: {data.get('benefits', data.get('key_benefits', ['Brightening', 'Fades dark spots']))}
                How to Use: {data.get('how_to_use', data.get('usage', 'Apply 2-3 drops in the morning before sunscreen'))}
                Side Effects: {data.get('side_effects', data.get('safety', 'Mild tingling for sensitive skin'))}
                Price: {data.get('price', '₹699')}
                
                Create a complete, compelling product page:"""
                
                # Use direct Gemini call
                response = self._call_direct_gemini(user_prompt, system_prompt)
                
                # Extract JSON from response
                json_str = self._extract_json_from_response(response)
                
                if json_str:
                    try:
                        page_data = json.loads(json_str)
                        
                        # Validate with ProductPage model
                        product_page = ProductPage(**page_data)
                        
                        return json.dumps({
                            "product_page": product_page.model_dump(),
                            "sections": len([k for k in page_data.keys() if k.endswith('_section')]),
                            "status": "success",
                            "method": "gemini_direct"
                        }, indent=2)
                    except Exception as e:
                        print(f"Error validating product page: {e}")
                        # Continue with raw data
                        return json.dumps({
                            "product_page": page_data,
                            "sections": len([k for k in page_data.keys() if k.endswith('_section')]),
                            "status": "success_unvalidated",
                            "error": str(e)
                        }, indent=2)
                else:
                    # Generate fallback product page
                    return self._generate_fallback_product_page(data)
                
            except Exception as e:
                print(f"Error generating product page: {e}")
                return self._generate_fallback_product_page(data)
        
        self.tools = [
            Tool(
                name="generate_faq_content",
                func=generate_faq_content,
                description="Generate FAQ content from questions and product data. Accepts JSON or text."
            ),
            Tool(
                name="generate_product_page",
                func=generate_product_page,
                description="Generate complete product page with all sections. Accepts JSON or text product data."
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
            json_match = re.search(r'(\{\s*".*"\s*:\s*.*?\})', response, re.DOTALL)
            if json_match:
                return json_match.group(1)
            return None
    
    def _generate_fallback_faq(self, questions: List, product_data: Dict) -> List[Dict]:
        """Generate fallback FAQ if Gemini fails"""
        faq_items = []
        
        default_questions = [
            "What is this product and what does it do?",
            "How do I use this product?",
            "Are there any side effects or precautions?",
            "Who should use this product?",
            "How long does it take to see results?"
        ]
        
        for i, q in enumerate(default_questions[:5]):
            answer = self._generate_faq_answer(q, product_data)
            faq_items.append({
                "question": q,
                "answer": answer,
                "category": ["informational", "usage", "safety", "safety", "effectiveness"][i],
                "tags": ["introduction", "usage", "safety", "suitability", "results"]
            })
        
        return faq_items
    
    def _generate_faq_answer(self, question: str, product_data: Dict) -> str:
        """Generate answer for a specific question"""
        name = product_data.get('name', 'this product')
        ingredients = product_data.get('key_ingredients', [])
        benefits = product_data.get('benefits', [])
        
        if "what is" in question.lower():
            return f"{name} is a skincare serum containing {', '.join(ingredients[:2]) if ingredients else 'key ingredients'}. It helps with {', '.join(benefits[:2]) if benefits else 'multiple skin benefits'}."
        elif "how do i use" in question.lower():
            usage = product_data.get('how_to_use', 'Apply as directed')
            return f"{usage}. For best results, use consistently as part of your daily skincare routine."
        elif "side effects" in question.lower():
            side_effects = product_data.get('side_effects', 'Mild tingling may occur')
            return f"{side_effects}. Always patch test before first use. Discontinue if irritation persists."
        elif "who should use" in question.lower():
            skin_type = product_data.get('skin_type', 'various skin types')
            return f"This product is suitable for {skin_type}. Those with specific conditions should consult a dermatologist."
        else:
            return f"With regular use, visible improvements can typically be seen within 2-4 weeks, though individual results may vary."
    
    def _generate_missing_faq_items(self, product_data: Dict, count: int) -> List[Dict]:
        """Generate additional FAQ items if needed"""
        additional = [
            {
                "question": "Can this product be used with other skincare products?",
                "answer": f"Yes, {product_data.get('name', 'this product')} can be layered with most skincare products. Apply after cleansing and before moisturizer.",
                "category": "usage",
                "tags": ["compatibility", "routine"]
            },
            {
                "question": "How should I store this product?",
                "answer": "Store in a cool, dry place away from direct sunlight. Keep the lid tightly closed to preserve efficacy.",
                "category": "usage",
                "tags": ["storage", "preservation"]
            }
        ]
        return additional[:count]
    
    def _generate_fallback_product_page(self, product_data: Dict) -> str:
        """Generate fallback product page template"""
        template_page = {
            "title": product_data.get('name', 'GlowBoost Vitamin C Serum'),
            "meta_description": f"{product_data.get('name', 'Professional skincare serum')} for {product_data.get('skin_type', 'all skin types')}. Provides {', '.join(product_data.get('benefits', ['multiple benefits']))}.",
            "hero_section": {
                "headline": product_data.get('name', 'GlowBoost Vitamin C Serum'),
                "subheadline": f"Professional {product_data.get('concentration', '10% Vitamin C')} serum for {product_data.get('skin_type', 'radiant skin')}",
                "key_points": product_data.get('benefits', ['Brightening', 'Hydrating', 'Even skin tone'])
            },
            "benefits_section": [
                {
                    "benefit": benefit,
                    "description": f"Helps improve {benefit.lower()} through advanced formulation",
                    "scientific_basis": "Clinically studied ingredients with proven efficacy"
                }
                for benefit in product_data.get('benefits', ['Brightening', 'Hydration'])[:3]
            ],
            "ingredients_section": [
                {
                    "ingredient": ingredient,
                    "purpose": "Key active ingredient",
                    "benefits": ["Antioxidant protection", "Skin rejuvenation"]
                }
                for ingredient in product_data.get('key_ingredients', ['Vitamin C', 'Hyaluronic Acid'])[:3]
            ],
            "usage_section": {
                "instructions": product_data.get('how_to_use', 'Apply 2-3 drops to cleansed skin'),
                "frequency": "Once daily, preferably in the morning",
                "best_practices": ["Patch test first", "Apply before sunscreen", "Use consistently"]
            },
            "safety_section": {
                "side_effects": product_data.get('side_effects', 'Mild tingling possible'),
                "precautions": "Avoid if allergic to any ingredients",
                "contraindications": "Not for broken or irritated skin"
            },
            "pricing_section": {
                "price": product_data.get('price', '₹699'),
                "value_proposition": "Professional-grade results at an accessible price",
                "comparison_value": "More affordable than clinical treatments"
            },
            "cta_section": {
                "primary_cta": "Buy Now",
                "secondary_cta": "Learn More",
                "urgency_message": "Limited stock available"
            }
        }
        
        return json.dumps({
            "product_page": template_page,
            "sections": 7,
            "status": "fallback_template"
        }, indent=2)
    
    def _setup_agent(self):
        """Setup content creator agent - Simplified for Gemini"""
        self.agent_executor = self._create_agent_executor(
            tools=self.tools,
            system_prompt=self.get_system_prompt()
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Content Creator Agent specialized in skincare products.
        
        Available tools:
        1. generate_faq_content - Creates FAQ from questions and product data
        2. generate_product_page - Creates complete product pages
        
        Always choose the right tool based on the request:
        - If asked for FAQ or questions: use generate_faq_content
        - If asked for product page or description: use generate_product_page
        
        Guidelines:
        • Use ONLY provided data, don't invent facts
        • Maintain professional, trustworthy tone
        • Ensure content is helpful and accurate"""
    
    # Simple helper methods for direct use
    def create_faq_simple(self, questions: List, product_data: Dict) -> List[Dict]:
        """Simple method to create FAQ without agent complexity"""
        try:
            input_data = {"questions": questions, "product_data": product_data}
            result = self.run_with_json_output(input_data)
            
            if result["success"] and result["output"]:
                output = result["output"]
                if isinstance(output, dict) and "faq_items" in output:
                    return output["faq_items"][:5]
                elif isinstance(output, list):
                    return output[:5]
        except Exception as e:
            print(f"Error creating FAQ: {e}")
        
        return self._generate_fallback_faq(questions, product_data)[:5]
    
    def create_product_page_simple(self, product_data: Dict) -> Dict:
        """Simple method to create product page without agent complexity"""
        try:
            result = self.run_with_json_output(product_data)
            
            if result["success"] and result["output"]:
                output = result["output"]
                if isinstance(output, dict):
                    return output
        except Exception as e:
            print(f"Error creating product page: {e}")
        
        # Return fallback
        fallback = json.loads(self._generate_fallback_product_page(product_data))
        return fallback.get("product_page", {})
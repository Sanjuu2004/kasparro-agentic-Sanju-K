from typing import Dict, Any, List
from langchain.tools import Tool
from langchain_core.output_parsers import JsonOutputParser
import json
import re

from src.agents.base_agent import BaseAgent
from src.core.models import ProductData, ComparisonPage


class ProductComparatorAgent(BaseAgent):
    """Agent for creating fictional products and comparisons - Updated for Gemini"""
    
    def __init__(self, llm=None):
        super().__init__(
            name="product_comparator",
            description="Creates fictional products and generates comparisons",
            llm=llm
        )
        self.json_parser = JsonOutputParser()
    
    def _setup_tools(self):
        """Setup comparison tools - Simplified for Gemini"""
        
        def create_fictional_product(main_product_data: str) -> str:
            """Create a fictional product for comparison - Gemini version"""
            try:
                # Parse product data
                if isinstance(main_product_data, str):
                    try:
                        data = json.loads(main_product_data)
                    except:
                        # Handle text input
                        data = {"description": main_product_data, "name": "Main Product"}
                else:
                    data = main_product_data
                
                # System prompt for creating fictional product
                system_prompt = """You are a skincare product developer creating a fictional contrasting product.
                
                Create a fictional skincare product that meaningfully contrasts with the main product.
                Make it DIFFERENT but realistic (not obviously inferior).
                
                Return ONLY valid JSON in this exact structure:
                {
                  "name": "Product Name",
                  "concentration": "XX% Active Ingredient",
                  "skin_type": ["Type1", "Type2"],
                  "key_ingredients": ["Ingredient1", "Ingredient2", "Ingredient3"],
                  "benefits": ["Benefit1", "Benefit2", "Benefit3"],
                  "how_to_use": "Usage instructions",
                  "side_effects": "Possible side effects",
                  "price": "₹XXX"
                }
                
                Guidelines:
                1. Make it contrast with main product (different ingredients, benefits, or skin type)
                2. Keep it realistic and plausible
                3. Price should be different (higher or lower)
                4. Include 3+ key ingredients and benefits
                5. Ensure side effects are reasonable"""
                
                user_prompt = f"""Create a fictional contrasting product for comparison with:
                
                Main Product: {data.get('name', 'Main Skincare Product')}
                Main Ingredients: {data.get('key_ingredients', data.get('ingredients', 'Various'))}
                Main Benefits: {data.get('benefits', data.get('key_benefits', 'Various'))}
                Main Skin Type: {data.get('skin_type', 'Various')}
                Main Price: {data.get('price', '₹XXX')}
                
                Create a fictional contrasting product:"""
                
                # Use direct Gemini call
                response = self._call_direct_gemini(user_prompt, system_prompt)
                
                # Extract JSON from response
                json_str = self._extract_json_from_response(response)
                
                if json_str:
                    try:
                        product_data = json.loads(json_str)
                        
                        # Validate with ProductData model
                        fictional_product = ProductData(**product_data)
                        
                        return json.dumps({
                            "fictional_product": fictional_product.model_dump(),
                            "status": "success",
                            "message": f"Created fictional product: {fictional_product.name}",
                            "method": "gemini_direct"
                        }, indent=2)
                    except Exception as e:
                        print(f"Error validating fictional product: {e}")
                        # Use raw data anyway
                        return json.dumps({
                            "fictional_product": product_data,
                            "status": "success_unvalidated",
                            "message": f"Created: {product_data.get('name', 'Fictional Product')}",
                            "error": str(e)
                        }, indent=2)
                else:
                    # Generate fallback fictional product
                    return self._generate_fallback_fictional_product(data)
                
            except Exception as e:
                print(f"Error creating fictional product: {e}")
                return self._generate_fallback_fictional_product(data)
        
        def generate_product_comparison(products_data: str) -> str:
            """Generate comparison between two products - Gemini version"""
            try:
                # Parse products data
                if isinstance(products_data, str):
                    try:
                        data = json.loads(products_data)
                    except:
                        # Handle text description
                        data = {"description": products_data}
                else:
                    data = products_data
                
                main_product = data.get("main_product", {})
                fictional_product = data.get("fictional_product", {})
                
                # If no fictional product, create one
                if not fictional_product:
                    fictional_result = json.loads(create_fictional_product(main_product))
                    fictional_product = fictional_result.get("fictional_product", {})
                
                # System prompt for comparison
                system_prompt = """You are a skincare expert creating detailed product comparisons.
                
                Create a comprehensive comparison table and analysis between two skincare products.
                
                Return ONLY valid JSON in this exact structure:
                {
                  "title": "Comparison: Product A vs Product B",
                  "products": [
                    {
                      "name": "Product A Name",
                      "type": "Serum/Cream/etc",
                      "key_ingredients": ["Ing1", "Ing2"],
                      "benefits": ["Benefit1", "Benefit2"],
                      "best_for": "Skin types or concerns",
                      "price": "₹XXX",
                      "rating": 4.5
                    },
                    {
                      "name": "Product B Name",
                      "type": "Serum/Cream/etc",
                      "key_ingredients": ["Ing1", "Ing2"],
                      "benefits": ["Benefit1", "Benefit2"],
                      "best_for": "Skin types or concerns",
                      "price": "₹XXX",
                      "rating": 4.0
                    }
                  ],
                  "comparison_points": [
                    {
                      "aspect": "Ingredients",
                      "product_a": "Description for Product A",
                      "product_b": "Description for Product B",
                      "winner": "A" or "B" or "Tie"
                    },
                    {
                      "aspect": "Effectiveness",
                      "product_a": "Description for Product A",
                      "product_b": "Description for Product B",
                      "winner": "A" or "B" or "Tie"
                    },
                    {
                      "aspect": "Value for Money",
                      "product_a": "Description for Product A",
                      "product_b": "Description for Product B",
                      "winner": "A" or "B" or "Tie"
                    },
                    {
                      "aspect": "Suitability",
                      "product_a": "Description for Product A",
                      "product_b": "Description for Product B",
                      "winner": "A" or "B" or "Tie"
                    },
                    {
                      "aspect": "Side Effects",
                      "product_a": "Description for Product A",
                      "product_b": "Description for Product B",
                      "winner": "A" or "B" or "Tie"
                    }
                  ],
                  "summary": "Overall comparison summary (2-3 paragraphs)",
                  "recommendation": "Who should choose which product and why"
                }
                
                Guidelines:
                1. Be objective and factual
                2. Highlight meaningful differences
                3. Include at least 5 comparison points
                4. Declare clear winners for each aspect
                5. Provide practical recommendations"""
                
                user_prompt = f"""Compare these two skincare products:
                
                PRODUCT A (Main):
                Name: {main_product.get('name', 'Product A')}
                Concentration: {main_product.get('concentration', 'Not specified')}
                Skin Type: {main_product.get('skin_type', 'Various')}
                Key Ingredients: {', '.join(main_product.get('key_ingredients', main_product.get('ingredients', ['Not specified']))[:3])}
                Benefits: {', '.join(main_product.get('benefits', main_product.get('key_benefits', ['Various']))[:3])}
                Price: {main_product.get('price', 'Not specified')}
                Side Effects: {main_product.get('side_effects', 'Not specified')}
                
                PRODUCT B (Fictional):
                Name: {fictional_product.get('name', 'Product B')}
                Concentration: {fictional_product.get('concentration', 'Not specified')}
                Skin Type: {fictional_product.get('skin_type', 'Various')}
                Key Ingredients: {', '.join(fictional_product.get('key_ingredients', fictional_product.get('ingredients', ['Not specified']))[:3])}
                Benefits: {', '.join(fictional_product.get('benefits', fictional_product.get('key_benefits', ['Various']))[:3])}
                Price: {fictional_product.get('price', 'Not specified')}
                Side Effects: {fictional_product.get('side_effects', 'Not specified')}
                
                Create a detailed, objective comparison:"""
                
                # Use direct Gemini call
                response = self._call_direct_gemini(user_prompt, system_prompt)
                
                # Extract JSON from response
                json_str = self._extract_json_from_response(response)
                
                if json_str:
                    try:
                        comparison_data = json.loads(json_str)
                        
                        # Try to validate with ComparisonPage model
                        try:
                            comparison_page = ComparisonPage(**comparison_data)
                            comparison_dict = comparison_page.model_dump()
                        except:
                            # Use raw data if validation fails
                            comparison_dict = comparison_data
                        
                        return json.dumps({
                            "comparison_page": comparison_dict,
                            "comparison_points": len(comparison_dict.get("comparison_points", [])),
                            "status": "success",
                            "method": "gemini_direct"
                        }, indent=2)
                    except Exception as e:
                        print(f"Error processing comparison: {e}")
                        return self._generate_fallback_comparison(main_product, fictional_product)
                else:
                    # Generate fallback comparison
                    return self._generate_fallback_comparison(main_product, fictional_product)
                
            except Exception as e:
                print(f"Error generating comparison: {e}")
                return self._generate_fallback_comparison(main_product, fictional_product)
        
        self.tools = [
            Tool(
                name="create_fictional_product",
                func=create_fictional_product,
                description="Create a fictional skincare product for comparison. Accepts JSON or text."
            ),
            Tool(
                name="generate_product_comparison",
                func=generate_product_comparison,
                description="Generate detailed comparison between two products. Accepts JSON or text."
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
    
    def _generate_fallback_fictional_product(self, main_product: Dict) -> str:
        """Generate fallback fictional product"""
        fictional_product = {
            "name": "RadiancePlus Niacinamide Serum",
            "concentration": "5% Niacinamide + 2% Zinc",
            "skin_type": ["All Skin Types", "Sensitive"],
            "key_ingredients": ["Niacinamide", "Zinc PCA", "Green Tea Extract", "Panthenol"],
            "benefits": ["Reduces redness", "Minimizes pores", "Improves skin texture", "Balances oil"],
            "how_to_use": "Apply 3-4 drops to clean face morning and night. Follow with moisturizer.",
            "side_effects": "Rare mild irritation. Discontinue if redness occurs.",
            "price": "₹899"
        }
        
        return json.dumps({
            "fictional_product": fictional_product,
            "status": "fallback",
            "message": f"Created fallback product: {fictional_product['name']}"
        }, indent=2)
    
    def _generate_fallback_comparison(self, product_a: Dict, product_b: Dict) -> str:
        """Generate fallback comparison"""
        comparison_data = {
            "title": f"Comparison: {product_a.get('name', 'Product A')} vs {product_b.get('name', 'Product B')}",
            "products": [
                {
                    "name": product_a.get('name', 'Product A'),
                    "type": "Vitamin C Serum",
                    "key_ingredients": product_a.get('key_ingredients', product_a.get('ingredients', ['Vitamin C', 'Hyaluronic Acid'])),
                    "benefits": product_a.get('benefits', product_a.get('key_benefits', ['Brightening', 'Antioxidant'])),
                    "best_for": product_a.get('skin_type', 'Oily, Combination skin'),
                    "price": product_a.get('price', '₹699'),
                    "rating": 4.5
                },
                {
                    "name": product_b.get('name', 'Product B'),
                    "type": "Niacinamide Serum",
                    "key_ingredients": product_b.get('key_ingredients', product_b.get('ingredients', ['Niacinamide', 'Zinc'])),
                    "benefits": product_b.get('benefits', product_b.get('key_benefits', ['Redness reduction', 'Pore minimization'])),
                    "best_for": product_b.get('skin_type', 'All skin types, Sensitive'),
                    "price": product_b.get('price', '₹899'),
                    "rating": 4.3
                }
            ],
            "comparison_points": [
                {
                    "aspect": "Active Ingredients",
                    "product_a": f"{product_a.get('concentration', '10% Vitamin C')} for brightening and antioxidant protection",
                    "product_b": f"{product_b.get('concentration', '5% Niacinamide')} for barrier repair and oil control",
                    "winner": "Tie",
                    "explanation": "Different ingredients for different concerns"
                },
                {
                    "aspect": "Skin Type Suitability",
                    "product_a": f"Best for {product_a.get('skin_type', 'oily and combination skin')}",
                    "product_b": f"Best for {product_b.get('skin_type', 'all skin types including sensitive')}",
                    "winner": "B",
                    "explanation": "Product B is more universally suitable"
                },
                {
                    "aspect": "Primary Benefits",
                    "product_a": f"{', '.join(product_a.get('benefits', ['Brightening', 'Dark spot reduction'])[:2])}",
                    "product_b": f"{', '.join(product_b.get('benefits', ['Redness reduction', 'Pore refinement'])[:2])}",
                    "winner": "Depends",
                    "explanation": "Choose based on your primary concern"
                },
                {
                    "aspect": "Price Value",
                    "product_a": f"{product_a.get('price', '₹699')} for Vitamin C formulation",
                    "product_b": f"{product_b.get('price', '₹899')} for Niacinamide blend",
                    "winner": "A",
                    "explanation": "Product A offers better value for money"
                },
                {
                    "aspect": "Side Effects & Safety",
                    "product_a": f"{product_a.get('side_effects', 'Mild tingling possible')}",
                    "product_b": f"{product_b.get('side_effects', 'Rare irritation')}",
                    "winner": "B",
                    "explanation": "Product B is generally better tolerated"
                }
            ],
            "summary": f"""This comparison highlights two different approaches to skincare: {product_a.get('name', 'Product A')} focuses on brightening and antioxidant protection with Vitamin C, while {product_b.get('name', 'Product B')} emphasizes barrier repair and oil control with Niacinamide.

Product A is particularly effective for addressing hyperpigmentation and providing antioxidant defense, making it ideal for those concerned with aging and sun damage. Product B excels at calming inflammation, reducing redness, and refining pores, making it better for sensitive or acne-prone skin.

Both products are well-formulated and effective within their respective categories. The choice depends largely on individual skin concerns and type.""",
            "recommendation": """• Choose Product A if: Your primary concerns are dark spots, uneven skin tone, or antioxidant protection. You have oily or combination skin that can tolerate Vitamin C.

• Choose Product B if: You have sensitive skin, struggle with redness or inflammation, or want to minimize pores and control oil. It's also better for those new to active ingredients.

• Consider using both: Some users alternate between Vitamin C (morning) and Niacinamide (evening) for comprehensive skincare benefits."""
        }
        
        return json.dumps({
            "comparison_page": comparison_data,
            "comparison_points": len(comparison_data["comparison_points"]),
            "status": "fallback_template"
        }, indent=2)
    
    def _setup_agent(self):
        """Setup product comparator agent - Simplified for Gemini"""
        self.agent_executor = self._create_agent_executor(
            tools=self.tools,
            system_prompt=self.get_system_prompt()
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Product Comparison Agent for skincare products.
        
        Available tools:
        1. create_fictional_product - Create fictional contrasting product
        2. generate_product_comparison - Compare two products in detail
        
        Always use the appropriate tool:
        - When asked to create a comparison product: use create_fictional_product
        - When asked to compare products: use generate_product_comparison
        - When given two products: use generate_product_comparison
        
        Guidelines:
        • Create meaningful contrasts (different ingredients/benefits)
        • Be objective in comparisons
        • Highlight practical differences for consumers
        • Provide clear recommendations"""
    
    # Simple helper methods
    def create_fictional_product_simple(self, main_product: Dict) -> Dict:
        """Simple method to create fictional product"""
        try:
            result = self.run_with_json_output(main_product)
            if result["success"] and result["output"]:
                output = result["output"]
                if isinstance(output, dict) and "fictional_product" in output:
                    return output["fictional_product"]
                return output
        except Exception as e:
            print(f"Error creating fictional product: {e}")
        
        # Return fallback
        fallback = json.loads(self._generate_fallback_fictional_product(main_product))
        return fallback.get("fictional_product", {})
    
    def create_comparison_simple(self, product_a: Dict, product_b: Dict = None) -> Dict:
        """Simple method to create comparison"""
        try:
            input_data = {"main_product": product_a}
            if product_b:
                input_data["fictional_product"] = product_b
            
            result = self.run_with_json_output(input_data)
            if result["success"] and result["output"]:
                output = result["output"]
                if isinstance(output, dict) and "comparison_page" in output:
                    return output["comparison_page"]
                return output
        except Exception as e:
            print(f"Error creating comparison: {e}")
        
        # Return fallback
        if not product_b:
            product_b = self.create_fictional_product_simple(product_a)
        fallback = json.loads(self._generate_fallback_comparison(product_a, product_b))
        return fallback.get("comparison_page", {})
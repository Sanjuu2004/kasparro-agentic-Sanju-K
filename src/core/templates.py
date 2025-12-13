from typing import Dict, Any, List
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate


class ContentTemplates:
    """LLM prompt templates for content generation"""
    
    @staticmethod
    def get_question_generation_template() -> ChatPromptTemplate:
        """Template for generating categorized questions"""
        system_template = """You are a skincare expert and market researcher. 
        Generate {num_questions} categorized questions about the given skincare product.
        
        Guidelines:
        1. Questions must be based ONLY on the provided product data
        2. Distribute questions across these categories: {categories}
        3. Each question should be specific and relevant to the product
        4. Include questions about ingredients, usage, safety, and effectiveness
        5. Do NOT invent new facts beyond the provided data
        
        Output Format: JSON list with 'question', 'category', and 'priority' fields"""
        
        human_template = """Product Data:
        Name: {name}
        Concentration: {concentration}
        Skin Type: {skin_type}
        Key Ingredients: {key_ingredients}
        Benefits: {benefits}
        How to Use: {how_to_use}
        Side Effects: {side_effects}
        Price: {price}
        
        Generate {num_questions} categorized questions."""
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_faq_generation_template() -> ChatPromptTemplate:
        """Template for generating FAQ answers"""
        system_template = """You are a skincare expert creating FAQ content.
        For each question, provide a helpful, accurate answer using ONLY the product data.
        
        Guidelines:
        1. Answers must be factual and based ONLY on provided data
        2. Keep answers concise (2-3 sentences)
        3. Address the specific question directly
        4. Do NOT add new information or claims
        5. Include relevant details from product data
        
        Output Format: JSON list with 'question', 'answer', 'category', and 'tags' fields"""
        
        human_template = """Product Context:
        Product: {name}
        Concentration: {concentration}
        Key Ingredients: {key_ingredients}
        Benefits: {benefits}
        Skin Type: {skin_type}
        
        Questions to Answer:
        {questions}
        
        Generate helpful FAQ answers."""
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_product_page_template() -> ChatPromptTemplate:
        """Template for generating product page content"""
        system_template = """You are a professional skincare copywriter creating product pages.
        Create a compelling, accurate product page using ONLY the provided data.
        
        Required Sections:
        1. Title and meta description
        2. Hero section with headline
        3. Benefits section (expand each benefit)
        4. Ingredients section (explain each ingredient)
        5. Usage instructions
        6. Safety information
        7. Pricing and value proposition
        
        Guidelines:
        - Use ONLY provided facts
        - Maintain professional, trustworthy tone
        - Structure content for web presentation
        - Include all key information
        
        Output Format: JSON with specified sections"""
        
        human_template = """Product Data:
        Name: {name}
        Concentration: {concentration}
        Skin Type: {skin_type}
        Key Ingredients: {key_ingredients}
        Benefits: {benefits}
        How to Use: {how_to_use}
        Side Effects: {side_effects}
        Price: {price}
        
        Create a complete product page."""
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_comparison_template() -> ChatPromptTemplate:
        """Template for generating product comparison"""
        system_template = """You are a skincare analyst creating product comparisons.
        Compare the two products objectively using ONLY the provided data.
        
        Required Elements:
        1. Product summaries
        2. Comparison points (price, ingredients, benefits, etc.)
        3. Objective summary of differences
        4. Recommendations based on different needs
        
        Guidelines:
        - Compare similar aspects
        - Be objective and factual
        - Highlight key differences
        - Do NOT invent new facts
        
        Output Format: JSON with products, comparison_points, summary, and recommendation"""
        
        human_template = """Products to Compare:

        Product A (Main):
        Name: {product_a_name}
        Concentration: {product_a_concentration}
        Skin Type: {product_a_skin_type}
        Key Ingredients: {product_a_ingredients}
        Benefits: {product_a_benefits}
        Price: {product_a_price}

        Product B (Fictional - created for comparison):
        Name: {product_b_name}
        Concentration: {product_b_concentration}
        Skin Type: {product_b_skin_type}
        Key Ingredients: {product_b_ingredients}
        Benefits: {product_b_benefits}
        Price: {product_b_price}

        Create a detailed comparison."""
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    @staticmethod
    def get_fictional_product_template() -> ChatPromptTemplate:
        """Template for creating fictional comparison product"""
        system_template = """Create a fictional skincare product for comparison purposes.
        The product should be:
        1. Different from the main product in meaningful ways
        2. Structurally similar (same fields as main product)
        3. Plausible but distinct in formulation
        4. Useful for comparison learning
        
        Do NOT copy the main product. Create meaningful contrasts.
        
        Output Format: JSON with name, concentration, skin_type, key_ingredients, benefits, how_to_use, side_effects, price"""
        
        human_template = """Main Product (for reference):
        Name: {name}
        Concentration: {concentration}
        Skin Type: {skin_type}
        Key Ingredients: {key_ingredients}
        Benefits: {benefits}
        
        Create a fictional contrasting product."""
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
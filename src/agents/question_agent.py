from typing import List, Dict, Any
import random
from .base import BaseAgent, AgentResult
from ..core.models import GeneratedQuestion, QuestionCategory, ProductData
from ..core.state import state_manager


class QuestionGenerationAgent(BaseAgent):
    """Generates categorized user questions from product data"""
    
    def __init__(self):
        super().__init__("question_gen_v1", "Question Generation Agent")
        self.required_state_fields = ["product_data"]
    
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate categorized questions"""
        state = state_manager.get_state()
        product_data = state.product_data
        
        # Question templates by category
        question_templates = {
            QuestionCategory.INFORMATIONAL: [
                "What is {concentration}?",
                "How does {product} work?",
                "What are the main ingredients in {product}?",
                "Is {product} suitable for {skin_type} skin?",
                "How is {product} different from other serums?"
            ],
            QuestionCategory.SAFETY: [
                "Are there any side effects of using {product}?",
                "Is {product} safe for sensitive skin?",
                "Can I use {product} during pregnancy?",
                "What should I do if I experience {side_effects}?",
                "How should I store {product} to maintain efficacy?"
            ],
            QuestionCategory.USAGE: [
                "How do I use {product} in my skincare routine?",
                "How many drops of {product} should I use?",
                "Can I use {product} in the morning and evening?",
                "Should I apply {product} before or after moisturizer?",
                "How long does one bottle of {product} last?"
            ],
            QuestionCategory.PURCHASE: [
                "Where can I buy {product}?",
                "Is {product} worth the price?",
                "Are there any discounts available for {product}?",
                "What is the return policy for {product}?",
                "How quickly will {product} ship?"
            ],
            QuestionCategory.COMPARISON: [
                "How does {product} compare to {ingredient} serums?",
                "Is {product} better than vitamin C powders?",
                "What makes {product} different from drugstore alternatives?",
                "Can {product} replace multiple products in my routine?"
            ],
            QuestionCategory.INGREDIENT: [
                "What type of Vitamin C is used in {product}?",
                "Is the {ingredient} in {product} stable?",
                "What concentration of {ingredient} is most effective?",
                "Are the ingredients in {product} vegan/cruelty-free?"
            ],
            QuestionCategory.EFFECTIVENESS: [
                "How long until I see results with {product}?",
                "Will {product} really {benefit}?",
                "What clinical studies support {product}'s claims?",
                "Can {product} help with specific concerns like {benefit}?"
            ]
        }
        
        generated_questions = []
        question_id = 1
        
        # Generate questions from each category
        for category, templates in question_templates.items():
            # Take 2-3 questions from each category
            selected_templates = random.sample(templates, min(3, len(templates)))
            
            for template in selected_templates:
                # Fill template with product data
                question_text = template.format(
                    product=product_data.name,
                    concentration=product_data.concentration,
                    skin_type=", ".join(product_data.skin_type),
                    side_effects=product_data.side_effects,
                    ingredient=product_data.key_ingredients[0] if product_data.key_ingredients else "key ingredient",
                    benefit=product_data.benefits[0] if product_data.benefits else "improve skin"
                )
                
                # Determine priority (1=highest, 5=lowest)
                priority = self._determine_priority(category, question_text)
                
                # Determine if expertise is required
                requires_expertise = category in [
                    QuestionCategory.SAFETY, 
                    QuestionCategory.INGREDIENT,
                    QuestionCategory.EFFECTIVENESS
                ]
                
                question = GeneratedQuestion(
                    id=f"Q{question_id:03d}",
                    question=question_text,
                    category=category,
                    priority=priority,
                    requires_expertise=requires_expertise
                )
                
                generated_questions.append(question)
                question_id += 1
        
        # Update state
        state_manager.update_state(generated_questions=generated_questions)
        
        return {
            "questions_generated": len(generated_questions),
            "categories_covered": list(set([q.category.value for q in generated_questions])),
            "questions": [q.model_dump() for q in generated_questions]
        }
    
    def _determine_priority(self, category: QuestionCategory, question: str) -> int:
        """Determine question priority"""
        high_priority_keywords = ["safe", "side effect", "pregnancy", "how to use", "price", "buy"]
        low_priority_keywords = ["compare", "difference", "vs", "alternative"]
        
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in high_priority_keywords):
            return 1
        elif category in [QuestionCategory.SAFETY, QuestionCategory.USAGE]:
            return 2
        elif any(keyword in question_lower for keyword in low_priority_keywords):
            return 4
        else:
            return 3
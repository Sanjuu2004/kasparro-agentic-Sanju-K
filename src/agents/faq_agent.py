from typing import Dict, Any, List
import random
from .base import BaseAgent
from ..core.models import FAQItem, QuestionCategory
from ..core.state import state_manager


class FAQGenerationAgent(BaseAgent):
    """Generates FAQ page from questions"""
    
    def __init__(self):
        super().__init__("faq_v1", "FAQ Generation Agent")
        self.required_state_fields = ["product_data", "generated_questions"]
        self.dependencies = ["question_generation"]
    
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate FAQ items from questions"""
        state = state_manager.get_state()
        product_data = state.product_data
        questions = state.generated_questions
        
        # Generate answers for questions
        faq_items = []
        
        # Answer templates by category
        answer_templates = {
            QuestionCategory.INFORMATIONAL: [
                "Our {product} contains {concentration} for optimal efficacy.",
                "{product} is specifically formulated for {skin_type} skin types.",
                "The key ingredients work synergistically to provide {benefits}."
            ],
            QuestionCategory.SAFETY: [
                "{product} is dermatologist-tested and safe for daily use.",
                "While {side_effects}, most users adapt within 1-2 weeks.",
                "We recommend patch testing if you have sensitive skin."
            ],
            QuestionCategory.USAGE: [
                "For best results: {how_to_use}",
                "Apply to clean, dry skin before moisturizer and sunscreen.",
                "Consistent daily use yields visible results in 4-6 weeks."
            ],
            QuestionCategory.PURCHASE: [
                "{product} is available at {price} with free shipping.",
                "Each bottle contains approximately 60 applications.",
                "We offer a 30-day satisfaction guarantee."
            ]
        }
        
        for question in questions[:8]:  # Take first 8 questions for FAQ
            # Select appropriate answer template
            templates = answer_templates.get(question.category, [
                "{product} is clinically formulated for optimal results."
            ])
            
            answer_template = random.choice(templates)
            
            # Fill template with product data
            answer = answer_template.format(
                product=product_data.name,
                concentration=product_data.concentration,
                skin_type=", ".join(product_data.skin_type),
                benefits=", ".join(product_data.benefits),
                side_effects=product_data.side_effects,
                how_to_use=product_data.how_to_use,
                price=product_data.price
            )
            
            # Add scientific backing for certain categories
            if question.category in [QuestionCategory.INGREDIENT, QuestionCategory.EFFECTIVENESS]:
                answer += " Clinical studies demonstrate significant improvement in skin parameters."
            
            faq_item = FAQItem(
                question=question.question,
                answer=answer,
                category=question.category.value,
                tags=self._generate_tags(question.category, product_data)
            )
            
            faq_items.append(faq_item)
        
        # Update state
        state_manager.update_state(faq_items=faq_items)
        
        return {
            "faq_items_generated": len(faq_items),
            "categories_covered": list(set([item.category for item in faq_items])),
            "example_questions": [item.question for item in faq_items[:3]]
        }
    
    def _generate_tags(self, category: QuestionCategory, product_data) -> List[str]:
        """Generate tags for FAQ items"""
        tags = [category.value]
        
        if "Vitamin C" in product_data.key_ingredients:
            tags.append("vitamin-c")
        if "Hyaluronic Acid" in product_data.key_ingredients:
            tags.append("hydration")
        
        tags.extend([benefit.lower().replace(" ", "-") for benefit in product_data.benefits[:2]])
        tags.extend([skin.lower() for skin in product_data.skin_type[:2]])
        
        return tags
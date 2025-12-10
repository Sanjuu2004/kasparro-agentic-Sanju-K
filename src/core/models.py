from typing import List, Dict, Optional, Any, TypedDict, Literal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ProductData(BaseModel):
    """Internal representation of product data"""
    name: str
    concentration: str
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: str
    price: str
    model_config = ConfigDict(frozen=True)  # Immutable for safety


class ContentBlockType(str, Enum):
    """Types of reusable content logic blocks"""
    BENEFITS_EXPANSION = "benefits_expansion"
    INGREDIENT_SCIENCE = "ingredient_science"
    USAGE_INSTRUCTIONS = "usage_instructions"
    SAFETY_GUIDELINES = "safety_guidelines"
    PRICE_JUSTIFICATION = "price_justification"
    COMPARISON_LOGIC = "comparison_logic"


class QuestionCategory(str, Enum):
    """Categories for generated questions"""
    INFORMATIONAL = "informational"
    SAFETY = "safety"
    USAGE = "usage"
    PURCHASE = "purchase"
    COMPARISON = "comparison"
    INGREDIENT = "ingredient"
    EFFECTIVENESS = "effectiveness"


class GeneratedQuestion(BaseModel):
    """Structure for generated questions"""
    id: str
    question: str
    category: QuestionCategory
    priority: int = Field(ge=1, le=5)  # 1=highest, 5=lowest
    requires_expertise: bool = False


class FAQItem(BaseModel):
    """FAQ Q&A structure"""
    question: str
    answer: str
    category: str
    tags: List[str] = []


class ProductPage(BaseModel):
    """Complete product page structure"""
    title: str
    meta_description: str
    hero_section: Dict[str, str]
    benefits_section: List[Dict[str, str]]
    ingredients_section: List[Dict[str, str]]
    usage_section: Dict[str, Any]
    safety_section: Dict[str, Any]
    pricing_section: Dict[str, Any]
    cta_section: Dict[str, str]


class ComparisonMatrix(BaseModel):
    """Comparison page structure"""
    products: List[Dict[str, Any]]
    comparison_points: List[Dict[str, Any]]
    summary: str
    recommendation: str


class AgentMessage(BaseModel):
    """Message structure for agent communication"""
    sender: str
    receiver: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class SystemState:
    """Global state container for the pipeline"""
    product_data: ProductData
    generated_questions: List[GeneratedQuestion] = None
    content_blocks: Dict[ContentBlockType, Any] = None
    faq_items: List[FAQItem] = None
    product_page: Optional[ProductPage] = None
    comparison_page: Optional[ComparisonMatrix] = None
    agent_messages: List[AgentMessage] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.generated_questions is None:
            self.generated_questions = []
        if self.content_blocks is None:
            self.content_blocks = {}
        if self.faq_items is None:
            self.faq_items = []
        if self.agent_messages is None:
            self.agent_messages = []
        if self.errors is None:
            self.errors = []
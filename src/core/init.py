"""
Core components: models, templates, and tools
"""

from src.core.models import (
    ProductData,
    QuestionCategory,
    GeneratedQuestion,
    FAQItem,
    ProductPage,
    ComparisonPage
)

from src.core.templates import ContentTemplates
from src.core.tools import (
    ParseProductDataTool,
    GenerateQuestionsTool,
    CreateFictionalProductTool,
    GenerateFAQTool,
    GenerateProductPageTool,
    GenerateComparisonTool
)

__all__ = [
    "ProductData",
    "QuestionCategory",
    "GeneratedQuestion",
    "FAQItem",
    "ProductPage",
    "ComparisonPage",
    "ContentTemplates",
    "ParseProductDataTool",
    "GenerateQuestionsTool",
    "CreateFictionalProductTool",
    "GenerateFAQTool",
    "GenerateProductPageTool",
    "GenerateComparisonTool"
]
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ProductData(BaseModel):
    """Product data model with validation"""
    name: str = Field(..., description="Product name")
    concentration: str = Field(..., description="Active ingredient concentration")
    skin_type: List[str] = Field(..., description="Suitable skin types")
    key_ingredients: List[str] = Field(..., description="Key ingredients")
    benefits: List[str] = Field(..., description="Product benefits")
    how_to_use: str = Field(..., description="Usage instructions")
    side_effects: str = Field(..., description="Potential side effects")
    price: str = Field(..., description="Product price")


class QuestionCategory(str, Enum):
    """Question categories as specified in requirements"""
    INFORMATIONAL = "informational"
    SAFETY = "safety"
    USAGE = "usage"
    PURCHASE = "purchase"
    COMPARISON = "comparison"
    INGREDIENT = "ingredient"
    EFFECTIVENESS = "effectiveness"


class GeneratedQuestion(BaseModel):
    """Generated question model"""
    question: str = Field(..., description="The question text")
    category: QuestionCategory = Field(..., description="Question category")
    priority: int = Field(default=3, ge=1, le=5, description="Priority 1-5")


class FAQItem(BaseModel):
    """FAQ item model"""
    question: str = Field(..., description="FAQ question")
    answer: str = Field(..., description="FAQ answer")
    category: str = Field(..., description="Question category")
    tags: List[str] = Field(default_factory=list, description="Content tags")


class ProductPage(BaseModel):
    """Complete product page model"""
    title: str = Field(..., description="Page title")
    meta_description: str = Field(..., description="SEO meta description")
    hero_section: Dict[str, str] = Field(..., description="Hero section content")
    benefits_section: List[Dict[str, str]] = Field(..., description="Benefits section")
    ingredients_section: List[Dict[str, Any]] = Field(..., description="Ingredients section")
    usage_section: Dict[str, Any] = Field(..., description="Usage instructions")
    safety_section: Dict[str, Any] = Field(..., description="Safety information")
    pricing_section: Dict[str, Any] = Field(..., description="Pricing information")


class ComparisonPage(BaseModel):
    """Product comparison page model"""
    products: List[Dict[str, Any]] = Field(..., description="Products being compared")
    comparison_points: List[Dict[str, Any]] = Field(..., description="Comparison metrics")
    summary: str = Field(..., description="Comparison summary")
    recommendation: str = Field(..., description="Recommendation based on comparison")
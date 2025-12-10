from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum
import json
from dataclasses import dataclass
from .models import ContentBlockType
from .logic_blocks import LogicBlockFactory


class TemplateFieldType(str, Enum):
    """Types of template fields"""
    TEXT = "text"
    LIST = "list"
    DICT = "dict"
    NESTED = "nested"
    COMPUTED = "computed"
    REFERENCE = "reference"


class FieldRule(BaseModel):
    """Rule for template field validation/transformation"""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    required: bool = True
    default: Any = None
    transform: Optional[Callable] = None
    validate: Optional[Callable] = None


class TemplateField(BaseModel):
    """Definition of a template field"""
    name: str
    field_type: TemplateFieldType
    description: str
    source: Optional[str] = None  # 'data', 'block:type', 'computed', 'reference'
    rules: FieldRule = Field(default_factory=FieldRule)
    dependencies: List[str] = []  # Other fields this depends on


class ContentTemplate(BaseModel):
    """Base content template"""
    template_id: str
    name: str
    version: str = "1.0"
    fields: Dict[str, TemplateField]
    field_order: List[str]
    post_processors: List[Callable] = []
    
    def render(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Render template with context"""
        result = {}
        
        # First pass: collect all field values
        field_values = {}
        for field_name in self.field_order:
            field = self.fields[field_name]
            value = self._resolve_field(field, context)
            
            # Apply transformations
            if field.rules.transform:
                value = field.rules.transform(value)
            
            # Validate
            if field.rules.validate:
                if not field.rules.validate(value):
                    raise ValueError(f"Validation failed for field {field_name}")
            
            field_values[field_name] = value
        
        # Second pass: apply dependencies and structure
        for field_name, field in self.fields.items():
            if field.field_type == TemplateFieldType.COMPUTED:
                # Compute based on other fields
                dep_values = {dep: field_values[dep] for dep in field.dependencies}
                value = self._compute_field(field, dep_values, context)
            else:
                value = field_values[field_name]
            
            # Apply field type formatting
            value = self._format_value(field.field_type, value)
            result[field_name] = value
        
        # Apply post-processors
        for processor in self.post_processors:
            result = processor(result, context)
        
        return result
    
    def _resolve_field(self, field: TemplateField, context: Dict[str, Any]) -> Any:
        """Resolve field value from source"""
        if field.source.startswith("block:"):
            # Get from logic block
            block_type = ContentBlockType(field.source.split(":")[1])
            block_result = LogicBlockFactory.execute_block(
                block_type, 
                context.get("product_data"),
                context
            )
            return block_result
        elif field.source == "data":
            # Get from product data
            return context.get("product_data", {}).get(field.name)
        elif field.source == "context":
            # Get from context
            return context.get(field.name)
        elif field.source == "computed":
            # Will be computed in second pass
            return None
        else:
            return field.rules.default
    
    def _compute_field(self, field: TemplateField, dependencies: Dict[str, Any], 
                      context: Dict[str, Any]) -> Any:
        """Compute field value from dependencies"""
        # Default computation - can be overridden
        if field.name == "summary":
            return self._compute_summary(dependencies)
        elif field.name == "meta_description":
            return self._compute_meta_description(dependencies)
        return dependencies
    
    def _compute_summary(self, dependencies: Dict[str, Any]) -> str:
        """Compute summary from dependencies"""
        product_name = dependencies.get("product_name", "Product")
        benefits = dependencies.get("benefits", [])
        if isinstance(benefits, list) and benefits:
            benefit_str = ", ".join([b.get("benefit", "") if isinstance(b, dict) else str(b) 
                                   for b in benefits[:2]])
            return f"{product_name} provides {benefit_str} through advanced formulation."
        return f"{product_name} - Advanced skincare solution"
    
    def _compute_meta_description(self, dependencies: Dict[str, Any]) -> str:
        """Compute meta description"""
        product_name = dependencies.get("product_name", "Skincare product")
        key_features = []
        
        if "concentration" in dependencies:
            key_features.append(dependencies["concentration"])
        if "key_ingredients" in dependencies:
            if isinstance(dependencies["key_ingredients"], list):
                key_features.append(f"with {', '.join(dependencies['key_ingredients'][:2])}")
        
        desc = f"{product_name} - {', '.join(key_features)}. "
        
        if "benefits" in dependencies:
            benefits = dependencies["benefits"]
            if isinstance(benefits, list) and benefits:
                benefit_list = [b.get("benefit", "") if isinstance(b, dict) else str(b) 
                              for b in benefits[:3]]
                desc += f"Benefits include {', '.join(benefit_list)}. "
        
        desc += "Shop now for glowing skin."
        return desc[:160]  # Truncate for SEO
    
    def _format_value(self, field_type: TemplateFieldType, value: Any) -> Any:
        """Format value based on field type"""
        if field_type == TemplateFieldType.TEXT:
            return str(value) if value is not None else ""
        elif field_type == TemplateFieldType.LIST:
            if isinstance(value, list):
                return value
            return [value] if value is not None else []
        elif field_type == TemplateFieldType.DICT:
            if isinstance(value, dict):
                return value
            return {field_type: value} if value is not None else {}
        return value


class FAQTemplate(ContentTemplate):
    """FAQ page template"""
    
    def __init__(self):
        fields = {
            "page_title": TemplateField(
                name="page_title",
                field_type=TemplateFieldType.TEXT,
                description="FAQ page title",
                source="computed",
                rules=FieldRule(default="Frequently Asked Questions")
            ),
            "meta_description": TemplateField(
                name="meta_description",
                field_type=TemplateFieldType.TEXT,
                description="SEO meta description",
                source="computed"
            ),
            "faq_items": TemplateField(
                name="faq_items",
                field_type=TemplateFieldType.LIST,
                description="List of Q&A items",
                source="context",
                rules=FieldRule(min_length=1)
            ),
            "categories": TemplateField(
                name="categories",
                field_type=TemplateFieldType.LIST,
                description="FAQ categories",
                source="computed"
            ),
            "last_updated": TemplateField(
                name="last_updated",
                field_type=TemplateFieldType.TEXT,
                description="Last update date",
                source="context",
                rules=FieldRule(default="Current date")
            )
        }
        
        super().__init__(
            template_id="faq_v1",
            name="FAQ Page Template",
            fields=fields,
            field_order=["page_title", "meta_description", "faq_items", "categories", "last_updated"]
        )
    
    def _compute_field(self, field: TemplateField, dependencies: Dict[str, Any], 
                      context: Dict[str, Any]) -> Any:
        """Override computation for FAQ specific fields"""
        if field.name == "page_title":
            product_name = context.get("product_data", {}).get("name", "Product")
            return f"{product_name} - Frequently Asked Questions"
        
        elif field.name == "categories":
            faq_items = dependencies.get("faq_items", [])
            categories = set()
            for item in faq_items:
                if isinstance(item, dict) and "category" in item:
                    categories.add(item["category"])
            return list(categories)
        
        return super()._compute_field(field, dependencies, context)
    
    def post_process(self, rendered: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """FAQ-specific post-processing"""
        # Sort FAQ items by category then by question
        if "faq_items" in rendered:
            rendered["faq_items"].sort(key=lambda x: (
                x.get("category", ""), 
                x.get("question", "")
            ))
        
        # Add structured data for SEO
        rendered["structured_data"] = self._generate_faq_schema(rendered["faq_items"])
        
        return rendered
    
    def _generate_faq_schema(self, faq_items: List[Dict]) -> Dict[str, Any]:
        """Generate FAQPage schema.org structured data"""
        schema_items = []
        for item in faq_items:
            schema_items.append({
                "@type": "Question",
                "name": item.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item.get("answer", "")
                }
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": schema_items
        }


class ProductPageTemplate(ContentTemplate):
    """Product page template"""
    
    def __init__(self):
        fields = {
            "product_name": TemplateField(
                name="product_name",
                field_type=TemplateFieldType.TEXT,
                description="Product name",
                source="data"
            ),
            "hero_headline": TemplateField(
                name="hero_headline",
                field_type=TemplateFieldType.TEXT,
                description="Hero section headline",
                source="computed"
            ),
            "hero_subheadline": TemplateField(
                name="hero_subheadline",
                field_type=TemplateFieldType.TEXT,
                description="Hero section subheadline",
                source="computed"
            ),
            "expanded_benefits": TemplateField(
                name="expanded_benefits",
                field_type=TemplateFieldType.LIST,
                description="Detailed benefits from block",
                source="block:benefits_expansion"
            ),
            "ingredient_profiles": TemplateField(
                name="ingredient_profiles",
                field_type=TemplateFieldType.LIST,
                description="Ingredient science profiles",
                source="block:ingredient_science"
            ),
            "safety_info": TemplateField(
                name="safety_info",
                field_type=TemplateFieldType.DICT,
                description="Safety guidelines",
                source="block:safety_guidelines"
            ),
            "price_analysis": TemplateField(
                name="price_analysis",
                field_type=TemplateFieldType.DICT,
                description="Price justification",
                source="block:price_justification"
            ),
            "how_to_use": TemplateField(
                name="how_to_use",
                field_type=TemplateFieldType.DICT,
                description="Usage instructions",
                source="data"
            ),
            "cta_primary": TemplateField(
                name="cta_primary",
                field_type=TemplateFieldType.TEXT,
                description="Primary call to action",
                source="computed",
                rules=FieldRule(default="Add to Cart")
            ),
            "cta_secondary": TemplateField(
                name="cta_secondary",
                field_type=TemplateFieldType.TEXT,
                description="Secondary call to action",
                source="computed",
                rules=FieldRule(default="Learn More")
            )
        }
        
        super().__init__(
            template_id="product_page_v1",
            name="Product Page Template",
            fields=fields,
            field_order=[
                "product_name", "hero_headline", "hero_subheadline",
                "expanded_benefits", "ingredient_profiles", "how_to_use",
                "safety_info", "price_analysis", "cta_primary", "cta_secondary"
            ]
        )
    
    def _compute_field(self, field: TemplateField, dependencies: Dict[str, Any], 
                      context: Dict[str, Any]) -> Any:
        """Product page specific computations"""
        product_data = context.get("product_data", {})
        
        if field.name == "hero_headline":
            name = product_data.get("name", "")
            concentration = product_data.get("concentration", "")
            return f"{concentration} {name} - Advanced Skin Transformation"
        
        elif field.name == "hero_subheadline":
            benefits = product_data.get("benefits", [])
            if benefits:
                benefit_str = " + ".join(benefits[:2])
                return f"Clinically formulated for {benefit_str}. Dermatologist tested."
            return "Professional-grade skincare for visible results."
        
        elif field.name == "how_to_use":
            usage = product_data.get("how_to_use", "")
            return {
                "instructions": usage,
                "frequency": "Daily, in morning routine",
                "application_tips": [
                    "Apply to clean, dry face",
                    "Use before moisturizer and sunscreen",
                    "Allow to absorb for 60 seconds before next product"
                ],
                "best_practices": [
                    "Store in cool, dark place",
                    "Use within 6 months of opening",
                    "Pair with sunscreen for best results"
                ]
            }
        
        elif field.name == "cta_primary":
            price = product_data.get("price", "")
            return f"Buy Now - {price}"
        
        elif field.name == "cta_secondary":
            return "Download Ingredient Guide"
        
        return super()._compute_field(field, dependencies, context)


class ComparisonTemplate(ContentTemplate):
    """Comparison page template"""
    
    def __init__(self):
        fields = {
            "page_title": TemplateField(
                name="page_title",
                field_type=TemplateFieldType.TEXT,
                description="Comparison page title",
                source="computed"
            ),
            "products": TemplateField(
                name="products",
                field_type=TemplateFieldType.LIST,
                description="Products to compare",
                source="context",
                rules=FieldRule(min_length=2, max_length=3)
            ),
            "comparison_points": TemplateField(
                name="comparison_points",
                field_type=TemplateFieldType.LIST,
                description="Points of comparison",
                source="computed"
            ),
            "key_differentiators": TemplateField(
                name="key_differentiators",
                field_type=TemplateFieldType.LIST,
                description="Key differences",
                source="computed"
            ),
            "recommendation": TemplateField(
                name="recommendation",
                field_type=TemplateFieldType.TEXT,
                description="Final recommendation",
                source="computed"
            ),
            "methodology": TemplateField(
                name="methodology",
                field_type=TemplateFieldType.TEXT,
                description="Comparison methodology",
                source="computed",
                rules=FieldRule(default="Based on ingredient analysis, concentration, and formulation")
            )
        }
        
        super().__init__(
            template_id="comparison_v1",
            name="Comparison Page Template",
            fields=fields,
            field_order=[
                "page_title", "products", "comparison_points", 
                "key_differentiators", "recommendation", "methodology"
            ]
        )
    
    def _compute_field(self, field: TemplateField, dependencies: Dict[str, Any], 
                      context: Dict[str, Any]) -> Any:
        """Comparison page specific computations"""
        products = dependencies.get("products", [])
        if not products or len(products) < 2:
            return super()._compute_field(field, dependencies, context)
        
        product_a = products[0]
        product_b = products[1]
        
        if field.name == "page_title":
            name_a = product_a.get("name", "Product A")
            name_b = product_b.get("name", "Product B")
            return f"{name_a} vs {name_b}: Detailed Comparison 2024"
        
        elif field.name == "comparison_points":
            return self._generate_comparison_points(product_a, product_b)
        
        elif field.name == "key_differentiators":
            return self._generate_differentiators(product_a, product_b)
        
        elif field.name == "recommendation":
            return self._generate_recommendation(product_a, product_b)
        
        return super()._compute_field(field, dependencies, context)
    
    def _generate_comparison_points(self, product_a: Dict, product_b: Dict) -> List[Dict]:
        """Generate comparison points"""
        points = []
        
        # Price comparison
        price_a = self._extract_price(product_a.get("price", ""))
        price_b = self._extract_price(product_b.get("price", ""))
        points.append({
            "category": "Price",
            "product_a": product_a.get("price", "N/A"),
            "product_b": product_b.get("price", "N/A"),
            "verdict": "Lower price" if price_a < price_b else 
                      "Higher price" if price_a > price_b else "Same price",
            "importance": "High"
        })
        
        # Ingredients comparison
        ing_a = set(product_a.get("key_ingredients", []))
        ing_b = set(product_b.get("key_ingredients", []))
        unique_a = ing_a - ing_b
        unique_b = ing_b - ing_a
        
        points.append({
            "category": "Key Ingredients",
            "product_a": list(ing_a),
            "product_b": list(ing_b),
            "verdict": f"{len(unique_a)} unique ingredients vs {len(unique_b)}",
            "importance": "Very High"
        })
        
        # Benefits comparison
        benefits_a = product_a.get("benefits", [])
        benefits_b = product_b.get("benefits", [])
        points.append({
            "category": "Primary Benefits",
            "product_a": benefits_a,
            "product_b": benefits_b,
            "verdict": f"{len(benefits_a)} vs {len(benefits_b)} claimed benefits",
            "importance": "High"
        })
        
        # Skin type suitability
        skin_a = product_a.get("skin_type", [])
        skin_b = product_b.get("skin_type", [])
        points.append({
            "category": "Skin Type Suitability",
            "product_a": skin_a,
            "product_b": skin_b,
            "verdict": "Check compatibility",
            "importance": "Medium"
        })
        
        # Concentration comparison
        conc_a = product_a.get("concentration", "")
        conc_b = product_b.get("concentration", "")
        points.append({
            "category": "Active Concentration",
            "product_a": conc_a,
            "product_b": conc_b,
            "verdict": "Higher concentration" if "10%" in conc_a else "Standard concentration",
            "importance": "High"
        })
        
        return points
    
    def _extract_price(self, price_str: str) -> float:
        """Extract numeric price"""
        import re
        match = re.search(r'[\d,]+', price_str)
        if match:
            return float(match.group().replace(',', ''))
        return 0.0
    
    def _generate_differentiators(self, product_a: Dict, product_b: Dict) -> List[Dict]:
        """Generate key differentiators"""
        differentiators = []
        
        # Concentration differentiator
        if "10%" in product_a.get("concentration", "") and "10%" not in str(product_b.get("concentration", "")):
            differentiators.append({
                "aspect": "Vitamin C Concentration",
                "advantage": "Product A",
                "reason": "10% is clinically effective range vs lower concentration in Product B",
                "impact": "Faster visible results"
            })
        
        # Ingredient differentiator
        ing_a = set(product_a.get("key_ingredients", []))
        ing_b = set(product_b.get("key_ingredients", []))
        unique_to_a = ing_a - ing_b
        unique_to_b = ing_b - ing_a
        
        if unique_to_a:
            differentiators.append({
                "aspect": "Unique Ingredients",
                "advantage": "Product A" if "Vitamin C" in unique_to_a else "Varies",
                "reason": f"Contains {', '.join(unique_to_a)} not found in Product B",
                "impact": "Targeted efficacy for specific concerns"
            })
        
        if unique_to_b:
            differentiators.append({
                "aspect": "Unique Ingredients",
                "advantage": "Product B",
                "reason": f"Contains {', '.join(unique_to_b)} not found in Product A",
                "impact": "Additional benefits"
            })
        
        # Price differentiator
        price_a = self._extract_price(product_a.get("price", ""))
        price_b = self._extract_price(product_b.get("price", ""))
        if price_a != price_b:
            differentiators.append({
                "aspect": "Price Value",
                "advantage": "Product A" if price_a < price_b else "Product B",
                "reason": f"₹{abs(price_a - price_b):.0f} {'less' if price_a < price_b else 'more'}",
                "impact": "Budget consideration"
            })
        
        return differentiators
    
    def _generate_recommendation(self, product_a: Dict, product_b: Dict) -> str:
        """Generate final recommendation"""
        # Simple recommendation logic based on features
        features_a = 0
        features_b = 0
        
        # Score based on concentration
        if "10%" in product_a.get("concentration", ""):
            features_a += 2
        if "10%" in product_b.get("concentration", ""):
            features_b += 2
        
        # Score based on key ingredients
        features_a += len(product_a.get("key_ingredients", []))
        features_b += len(product_b.get("key_ingredients", []))
        
        # Score based on benefits
        features_a += len(product_a.get("benefits", []))
        features_b += len(product_b.get("benefits", []))
        
        if features_a > features_b:
            return f"Recommend {product_a.get('name')} for its superior formulation and proven ingredients."
        elif features_b > features_a:
            return f"Recommend {product_b.get('name')} for its comprehensive benefits and unique ingredients."
        else:
            price_a = self._extract_price(product_a.get("price", ""))
            price_b = self._extract_price(product_b.get("price", ""))
            if price_a < price_b:
                return f"Recommend {product_a.get('name')} for better value at similar efficacy."
            else:
                return f"Recommend {product_b.get('name')} based on specific ingredient preferences."


class TemplateFactory:
    """Factory for template management"""
    
    _templates: Dict[str, ContentTemplate] = {}
    
    @classmethod
    def register_template(cls, template: ContentTemplate):
        """Register a template"""
        cls._templates[template.template_id] = template
    
    @classmethod
    def get_template(cls, template_id: str) -> ContentTemplate:
        """Get a template by ID"""
        if template_id not in cls._templates:
            raise ValueError(f"Template {template_id} not found")
        return cls._templates[template_id]
    
    @classmethod
    def render_template(cls, template_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Render a template with context"""
        template = cls.get_template(template_id)
        return template.render(context)


# Register templates
TemplateFactory.register_template(FAQTemplate())
TemplateFactory.register_template(ProductPageTemplate())
TemplateFactory.register_template(ComparisonTemplate())
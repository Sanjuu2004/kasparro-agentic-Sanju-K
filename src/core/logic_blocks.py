from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import re
from .models import ProductData, ContentBlockType
from .state import state_manager


@dataclass
class LogicBlock:
    """Base class for reusable content logic blocks"""
    block_type: ContentBlockType
    dependencies: List[ContentBlockType] = None
    version: str = "1.0"
    
    def execute(self, product_data: ProductData, context: Dict[str, Any] = None) -> Any:
        raise NotImplementedError


class BenefitsExpansionBlock(LogicBlock):
    """Expands benefits into detailed descriptions"""
    
    def __init__(self):
        super().__init__(ContentBlockType.BENEFITS_EXPANSION)
        self._benefit_templates = {
            "brightening": "Targets dullness by inhibiting melanin production, resulting in {intensity} brighter complexion within {timeframe}",
            "fades dark spots": "Reduces appearance of hyperpigmentation by {mechanism}, visibly improving spot clarity by {percentage}",
            "hydrating": "Increases skin moisture retention by {amount}, improving skin barrier function",
            "anti-aging": "Stimulates collagen production, reducing fine lines by {reduction}% over {period}"
        }
    
    def execute(self, product_data: ProductData, context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Expand each benefit with scientific backing"""
        expanded_benefits = []
        
        for benefit in product_data.benefits:
            normalized = benefit.lower().strip()
            template = self._benefit_templates.get(normalized, "{benefit} for {skin_type} skin")
            
            # Fill template based on product specifics
            if "brightening" in normalized:
                intensity = "noticeably" if "10%" in product_data.concentration else "gradually"
                timeframe = "2-4 weeks" if "Vitamin C" in product_data.key_ingredients else "4-6 weeks"
                description = template.format(intensity=intensity, timeframe=timeframe)
            elif "dark spots" in normalized:
                mechanism = "tyrosinase inhibition" if "Vitamin C" in product_data.key_ingredients else "cell turnover"
                percentage = "up to 40%" if "10%" in product_data.concentration else "up to 25%"
                description = template.format(mechanism=mechanism, percentage=percentage)
            else:
                description = template.format(benefit=benefit, skin_type=", ".join(product_data.skin_type))
            
            expanded_benefits.append({
                "benefit": benefit,
                "description": description,
                "scientific_basis": self._get_scientific_basis(benefit, product_data),
                "time_to_effect": self._estimate_timeframe(benefit),
                "ingredients_supporting": self._get_supporting_ingredients(benefit, product_data)
            })
        
        return expanded_benefits
    
    def _get_scientific_basis(self, benefit: str, product_data: ProductData) -> str:
        """Provide scientific basis for benefit"""
        if "Vitamin C" in product_data.key_ingredients:
            if "bright" in benefit.lower():
                return "L-ascorbic acid (Vitamin C) inhibits tyrosinase enzyme, reducing melanin synthesis"
            elif "spot" in benefit.lower():
                return "Vitamin C interrupts melanosome transfer to keratinocytes, lightening hyperpigmentation"
        return "Clinically studied ingredients promote skin health and appearance"
    
    def _estimate_timeframe(self, benefit: str) -> str:
        """Estimate time to see results"""
        if "bright" in benefit.lower():
            return "2-4 weeks with daily use"
        elif "spot" in benefit.lower():
            return "4-8 weeks for visible improvement"
        return "4-6 weeks for optimal results"
    
    def _get_supporting_ingredients(self, benefit: str, product_data: ProductData) -> List[str]:
        """Identify which ingredients support this benefit"""
        supporting = []
        for ingredient in product_data.key_ingredients:
            if "Vitamin C" in ingredient and ("bright" in benefit.lower() or "spot" in benefit.lower()):
                supporting.append(ingredient)
            elif "Hyaluronic" in ingredient and "hydrat" in benefit.lower():
                supporting.append(ingredient)
        return supporting


class IngredientScienceBlock(LogicBlock):
    """Provides scientific information about ingredients"""
    
    def __init__(self):
        super().__init__(ContentBlockType.INGREDIENT_SCIENCE)
        self._ingredient_db = {
            "Vitamin C": {
                "type": "Antioxidant",
                "function": "Collagen synthesis, photoprotection, brightening",
                "optimal_concentration": "10-20%",
                "stability": "Light and air sensitive",
                "synergies": ["Vitamin E", "Ferulic Acid"]
            },
            "Hyaluronic Acid": {
                "type": "Humectant",
                "function": "Moisture retention, plumping, barrier support",
                "molecular_weights": ["High (surface hydration)", "Low (deep penetration)"],
                "holding_capacity": "Up to 1000x its weight in water"
            }
        }
    
    def execute(self, product_data: ProductData, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate detailed ingredient profiles"""
        profiles = []
        
        for ingredient in product_data.key_ingredients:
            base_info = self._ingredient_db.get(ingredient, {
                "type": "Active Ingredient",
                "function": "Skin conditioning",
                "notes": "Key component in formulation"
            })
            
            # Add concentration-specific info
            concentration_info = self._extract_concentration(ingredient, product_data.concentration)
            
            profiles.append({
                "name": ingredient,
                "concentration": concentration_info,
                "primary_function": base_info["function"],
                "mechanism_of_action": self._get_mechanism(ingredient),
                "skin_type_suitability": self._get_skin_type_suitability(ingredient, product_data.skin_type),
                "clinical_evidence": self._get_evidence_level(ingredient),
                "formulation_notes": self._get_formulation_notes(ingredient, product_data)
            })
        
        return profiles
    
    def _extract_concentration(self, ingredient: str, concentration_text: str) -> str:
        """Extract concentration information"""
        if "Vitamin C" in ingredient and "%" in concentration_text:
            match = re.search(r'(\d+)%', concentration_text)
            if match:
                perc = match.group(1)
                return f"{perc}% (Effective range: 5-20%)"
        return "Proprietary blend"
    
    def _get_mechanism(self, ingredient: str) -> str:
        """Get mechanism of action"""
        mechanisms = {
            "Vitamin C": "Antioxidant protection by neutralizing free radicals, collagen synthesis via prolyl hydroxylase activation",
            "Hyaluronic Acid": "Binds water molecules in dermis and epidermis, creating hydration matrix"
        }
        return mechanisms.get(ingredient, "Improves skin condition through active delivery")
    
    def _get_skin_type_suitability(self, ingredient: str, skin_types: List[str]) -> List[str]:
        """Determine suitability for skin types"""
        suitability = []
        for skin_type in skin_types:
            if skin_type.lower() in ["oily", "combination"] and "Vitamin C" in ingredient:
                suitability.append(f"Suitable for {skin_type} (oil-free formulation)")
            elif skin_type.lower() in ["dry", "normal"] and "Hyaluronic" in ingredient:
                suitability.append(f"Excellent for {skin_type} (hydration boost)")
            else:
                suitability.append(f"Compatible with {skin_type}")
        return suitability
    
    def _get_evidence_level(self, ingredient: str) -> str:
        """Get clinical evidence level"""
        levels = {
            "Vitamin C": "Level 1A - Multiple RCTs demonstrating efficacy",
            "Hyaluronic Acid": "Level 1B - Strong clinical evidence for hydration"
        }
        return levels.get(ingredient, "Clinical studies support efficacy")
    
    def _get_formulation_notes(self, ingredient: str, product_data: ProductData) -> str:
        """Get formulation-specific notes"""
        notes = []
        if "Vitamin C" in ingredient:
            notes.append("L-ascorbic acid form for maximum bioavailability")
            if "Hyaluronic Acid" in product_data.key_ingredients:
                notes.append("Stabilized with hydrating agents to prevent irritation")
        if "Hyaluronic Acid" in ingredient:
            notes.append("Multi-molecular weight for layered hydration")
        return "; ".join(notes) if notes else "Optimized for stability and penetration"


class SafetyGuidelinesBlock(LogicBlock):
    """Generates safety guidelines and precautions"""
    
    def __init__(self):
        super().__init__(ContentBlockType.SAFETY_GUIDELINES)
    
    def execute(self, product_data: ProductData, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive safety information"""
        return {
            "general_warnings": self._generate_warnings(product_data),
            "skin_type_precautions": self._get_skin_type_precautions(product_data.skin_type),
            "ingredient_specific_cautions": self._get_ingredient_cautions(product_data.key_ingredients),
            "usage_restrictions": self._get_usage_restrictions(product_data),
            "first_aid_measures": self._get_first_aid_measures(),
            "storage_conditions": "Store below 25°C, protect from light and moisture",
            "shelf_life": "12 months unopened, 6 months after opening",
            "patch_test_instructions": self._get_patch_test_instructions(),
            "discontinuation_signs": ["Persistent redness", "Severe itching", "Swelling", "Rash"]
        }
    
    def _generate_warnings(self, product_data: ProductData) -> List[str]:
        """Generate product-specific warnings"""
        warnings = [
            "For external use only",
            "Avoid contact with eyes and mucous membranes",
            "Discontinue use if irritation occurs"
        ]
        
        if "Vitamin C" in product_data.key_ingredients:
            warnings.append("May cause temporary tingling on first use - this is normal")
            warnings.append("Can increase sun sensitivity - always use sunscreen")
        
        if "sensitive" in product_data.side_effects.lower():
            warnings.append("Patch test recommended for sensitive skin")
        
        return warnings
    
    def _get_skin_type_precautions(self, skin_types: List[str]) -> Dict[str, str]:
        """Get precautions for specific skin types"""
        precautions = {}
        for skin_type in skin_types:
            if skin_type.lower() == "oily":
                precautions[skin_type] = "Use in PM routine to assess tolerance"
            elif skin_type.lower() == "combination":
                precautions[skin_type] = "Apply only to affected areas, avoid dry zones"
            elif "sensitive" in skin_type.lower():
                precautions[skin_type] = "Begin with alternate day application"
        return precautions
    
    def _get_ingredient_cautions(self, ingredients: List[str]) -> List[Dict[str, str]]:
        """Get cautions for specific ingredients"""
        cautions = []
        for ingredient in ingredients:
            if "Vitamin C" in ingredient:
                cautions.append({
                    "ingredient": ingredient,
                    "caution": "Avoid combining with niacinamide in same routine (space by 30 minutes)",
                    "reason": "pH incompatibility may reduce efficacy"
                })
            if "Acid" in ingredient:
                cautions.append({
                    "ingredient": ingredient,
                    "caution": "Do not use with other exfoliating acids (AHA/BHA)",
                    "reason": "Risk of over-exfoliation and barrier damage"
                })
        return cautions
    
    def _get_usage_restrictions(self, product_data: ProductData) -> List[str]:
        """Get usage restrictions"""
        restrictions = ["Not recommended for children under 12"]
        
        if "pregnant" in product_data.side_effects.lower() or "breastfeeding" in product_data.side_effects.lower():
            restrictions.append("Consult physician before use during pregnancy or breastfeeding")
        
        return restrictions
    
    def _get_first_aid_measures(self) -> Dict[str, str]:
        """Get first aid measures"""
        return {
            "eye_contact": "Rinse immediately with plenty of water for 15 minutes. Seek medical attention if irritation persists.",
            "skin_irritation": "Wash with mild soap and water. Apply soothing cream if needed.",
            "ingestion": "Rinse mouth. Do not induce vomiting. Seek medical attention immediately."
        }
    
    def _get_patch_test_instructions(self) -> str:
        """Get patch test instructions"""
        return (
            "Apply small amount behind ear or inner forearm. Leave for 24 hours without washing. "
            "Check for redness, itching, or swelling. If no reaction occurs, product is safe for use."
        )


class PriceJustificationBlock(LogicBlock):
    """Generates price justification content"""
    
    def __init__(self):
        super().__init__(ContentBlockType.PRICE_JUSTIFICATION)
    
    def execute(self, product_data: ProductData, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate value proposition and price justification"""
        price_numeric = self._extract_price(product_data.price)
        
        return {
            "price_analysis": self._analyze_price(price_numeric),
            "value_proposition": self._generate_value_prop(product_data),
            "cost_breakdown": self._estimate_cost_breakdown(product_data),
            "competitive_positioning": self._get_competitive_position(price_numeric),
            "roi_calculation": self._calculate_roi(product_data),
            "quality_indicators": self._get_quality_indicators(product_data)
        }
    
    def _extract_price(self, price_str: str) -> float:
        """Extract numeric price from string"""
        import re
        match = re.search(r'[\d,]+', price_str)
        if match:
            price = match.group().replace(',', '')
            return float(price)
        return 699.0  # Default
    
    def _analyze_price(self, price: float) -> Dict[str, Any]:
        """Analyze price positioning"""
        if price < 500:
            tier = "Budget"
        elif price < 1000:
            tier = "Mid-range"
        elif price < 2000:
            tier = "Premium"
        else:
            tier = "Luxury"
        
        return {
            "price_tier": tier,
            "value_category": "Therapeutic" if price > 500 else "Maintenance",
            "affordability_score": self._calculate_affordability(price),
            "per_use_cost": round(price / 60, 2)  # Assuming 60 uses per bottle
        }
    
    def _calculate_affordability(self, price: float) -> str:
        """Calculate affordability score"""
        if price < 400:
            return "Highly Affordable"
        elif price < 800:
            return "Accessible"
        elif price < 1500:
            return "Premium Investment"
        else:
            return "Luxury Purchase"
    
    def _generate_value_prop(self, product_data: ProductData) -> List[str]:
        """Generate value propositions"""
        value_props = []
        
        if "10%" in product_data.concentration:
            value_props.append("Clinical-strength 10% Vitamin C concentration")
        
        if len(product_data.key_ingredients) >= 2:
            value_props.append(f"Synergistic blend of {len(product_data.key_ingredients)} actives")
        
        if "Hyaluronic Acid" in product_data.key_ingredients:
            value_props.append("Multi-depth hydration technology")
        
        value_props.append("Dermatologist-tested formula")
        value_props.append("Cruelty-free and vegan formulation")
        
        return value_props
    
    def _estimate_cost_breakdown(self, product_data: ProductData) -> Dict[str, str]:
        """Estimate cost breakdown"""
        breakdown = {
            "ingredients": "40-50%",
            "research_development": "15-20%",
            "packaging": "10-15%",
            "quality_control": "8-12%",
            "sustainability_initiatives": "5-8%",
            "profit_margin": "10-15%"
        }
        return breakdown
    
    def _get_competitive_position(self, price: float) -> Dict[str, Any]:
        """Get competitive positioning"""
        competitors = {
            "Budget": {"range": "₹200-₹500", "differentiator": "Basic formulations"},
            "Mid-range": {"range": "₹500-₹1500", "differentiator": "Clinical actives"},
            "Premium": {"range": "₹1500-₹5000", "differentiator": "Medical-grade"}
        }
        
        for tier, info in competitors.items():
            if price <= float(info["range"].split("-")[1].replace("₹", "")):
                return {
                    "position": f"Upper {tier}",
                    "differentiation": "Superior concentration and stability vs competition",
                    "target_audience": "Quality-conscious consumers seeking proven efficacy"
                }
        
        return {
            "position": "Premium",
            "differentiation": "Pharmaceutical-grade formulation",
            "target_audience": "Discerning consumers prioritizing results"
        }
    
    def _calculate_roi(self, product_data: ProductData) -> Dict[str, str]:
        """Calculate return on investment"""
        return {
            "skincare_routine_simplification": "Replaces 2-3 ordinary products",
            "time_savings": "2 minutes vs 6 minutes for multi-product routine",
            "preventive_value": "Potential savings on future corrective treatments",
            "confidence_boost": "Priceless emotional return"
        }
    
    def _get_quality_indicators(self, product_data: ProductData) -> List[Dict[str, str]]:
        """Get quality indicators"""
        indicators = [
            {
                "indicator": "Ingredient Purity",
                "evidence": "Pharmaceutical-grade sourcing",
                "impact": "Higher efficacy, lower irritation"
            },
            {
                "indicator": "Concentration Transparency",
                "evidence": "Exact percentage disclosed",
                "impact": "Predictable results"
            },
            {
                "indicator": "Stability Assurance",
                "evidence": "Airless packaging, antioxidant protection",
                "impact": "Maintains potency through shelf life"
            },
            {
                "indicator": "Skin Type Specificity",
                "evidence": "Formulated for oily/combination skin",
                "impact": "Targeted effectiveness"
            }
        ]
        return indicators


class LogicBlockFactory:
    """Factory for creating and managing logic blocks"""
    
    _registry: Dict[ContentBlockType, LogicBlock] = {}
    
    @classmethod
    def register_block(cls, block_type: ContentBlockType, block_class):
        """Register a logic block"""
        cls._registry[block_type] = block_class()
    
    @classmethod
    def get_block(cls, block_type: ContentBlockType) -> LogicBlock:
        """Get a logic block instance"""
        if block_type not in cls._registry:
            raise ValueError(f"Block type {block_type} not registered")
        return cls._registry[block_type]
    
    @classmethod
    def execute_block(cls, block_type: ContentBlockType, 
                     product_data: ProductData, 
                     context: Dict[str, Any] = None) -> Any:
        """Execute a logic block"""
        block = cls.get_block(block_type)
        return block.execute(product_data, context)


# Register all blocks
LogicBlockFactory.register_block(ContentBlockType.BENEFITS_EXPANSION, BenefitsExpansionBlock)
LogicBlockFactory.register_block(ContentBlockType.INGREDIENT_SCIENCE, IngredientScienceBlock)
LogicBlockFactory.register_block(ContentBlockType.SAFETY_GUIDELINES, SafetyGuidelinesBlock)
LogicBlockFactory.register_block(ContentBlockType.PRICE_JUSTIFICATION, PriceJustificationBlock)
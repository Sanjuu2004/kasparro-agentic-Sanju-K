import pytest
from src.core.models import ProductData
from src.core.logic_blocks import (
    BenefitsExpansionBlock,
    IngredientScienceBlock,
    LogicBlockFactory,
    ContentBlockType
)


@pytest.fixture
def sample_product_data():
    return ProductData(
        name="GlowBoost Vitamin C Serum",
        concentration="10% Vitamin C",
        skin_type=["Oily", "Combination"],
        key_ingredients=["Vitamin C", "Hyaluronic Acid"],
        benefits=["Brightening", "Fades dark spots"],
        how_to_use="Apply 2–3 drops in the morning before sunscreen",
        side_effects="Mild tingling for sensitive skin",
        price="₹699"
    )


def test_benefits_expansion_block(sample_product_data):
    block = BenefitsExpansionBlock()
    result = block.execute(sample_product_data)
    
    assert len(result) == 2
    assert result[0]["benefit"] == "Brightening"
    assert "description" in result[0]
    assert "scientific_basis" in result[0]
    assert "time_to_effect" in result[0]


def test_ingredient_science_block(sample_product_data):
    block = IngredientScienceBlock()
    result = block.execute(sample_product_data)
    
    assert len(result) == 2
    assert result[0]["name"] == "Vitamin C"
    assert "concentration" in result[0]
    assert "primary_function" in result[0]
    assert "mechanism_of_action" in result[0]


def test_logic_block_factory(sample_product_data):
    result = LogicBlockFactory.execute_block(
        ContentBlockType.BENEFITS_EXPANSION,
        sample_product_data
    )
    
    assert isinstance(result, list)
    assert len(result) > 0


def test_all_blocks_registered():
    registered_types = LogicBlockFactory._registry.keys()
    expected_types = [
        ContentBlockType.BENEFITS_EXPANSION,
        ContentBlockType.INGREDIENT_SCIENCE,
        ContentBlockType.SAFETY_GUIDELINES,
        ContentBlockType.PRICE_JUSTIFICATION
    ]
    
    for expected in expected_types:
        assert expected in registered_types
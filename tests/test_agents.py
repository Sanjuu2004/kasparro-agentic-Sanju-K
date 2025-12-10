import pytest
import asyncio
from pathlib import Path

from src.agents.ingestion_agent import DataIngestionAgent
from src.agents.question_agent import QuestionGenerationAgent
from src.core.state import state_manager


class TestAgents:
    
    @pytest.fixture
    def sample_data(self):
        return {
            "name": "GlowBoost Vitamin C Serum",
            "concentration": "10% Vitamin C",
            "skin_type": ["Oily", "Combination"],
            "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
            "benefits": ["Brightening", "Fades dark spots"],
            "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
            "side_effects": "Mild tingling for sensitive skin",
            "price": "₹699"
        }
    
    @pytest.mark.asyncio
    async def test_ingestion_agent(self, sample_data):
        agent = DataIngestionAgent()
        result = await agent.execute({"raw_product_data": sample_data})
        
        assert result.success
        assert result.data["product_parsed"] == True
        assert result.data["validation_passed"] == True
    
    @pytest.mark.asyncio
    async def test_question_agent(self, sample_data):
        # First initialize state
        state_manager.initialize_state(sample_data)
        
        agent = QuestionGenerationAgent()
        result = await agent.execute({})
        
        assert result.success
        assert result.data["questions_generated"] >= 15
        assert "categories_covered" in result.data
    
    def test_output_directory(self):
        output_dir = Path("outputs")
        assert output_dir.exists()
    
    def test_docs_directory(self):
        docs_dir = Path("docs")
        assert docs_dir.exists()
        assert (docs_dir / "projectdocumentation.md").exists()
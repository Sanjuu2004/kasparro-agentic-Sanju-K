from typing import Dict, Any
import json
from pathlib import Path
from .base import BaseAgent
from ..core.state import state_manager


class OutputGenerationAgent(BaseAgent):
    """Writes all generated content to JSON files"""
    
    def __init__(self):
        super().__init__("output_v1", "Output Generation Agent")
        self.required_state_fields = ["faq_items", "product_page", "comparison_page"]
        self.dependencies = ["faq_generation", "product_page", "comparison_page"]
    
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON output files"""
        state = state_manager.get_state()
        
        # Create output directory
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Prepare FAQ output
        faq_output = {
            "page_type": "faq",
            "product": state.product_data.name,
            "generated_at": context.get("timestamp", ""),
            "faq_items": [item.model_dump() for item in state.faq_items],
            "categories": list(set([item.category for item in state.faq_items])),
            "total_questions": len(state.faq_items)
        }
        
        # Write FAQ JSON
        faq_path = output_dir / "faq.json"
        with open(faq_path, 'w', encoding='utf-8') as f:
            json.dump(faq_output, f, indent=2, ensure_ascii=False)
        
        # Write Product Page JSON
        product_path = output_dir / "product_page.json"
        with open(product_path, 'w', encoding='utf-8') as f:
            json.dump(state.product_page, f, indent=2, ensure_ascii=False)
        
        # Write Comparison Page JSON
        comparison_path = output_dir / "comparison_page.json"
        with open(comparison_path, 'w', encoding='utf-8') as f:
            json.dump(state.comparison_page, f, indent=2, ensure_ascii=False)
        
        # Create execution summary
        summary = {
            "execution_summary": {
                "total_faq_items": len(state.faq_items),
                "product_page_sections": len(state.product_page) if state.product_page else 0,
                "comparison_points": len(state.comparison_page.get("comparison_points", [])) if state.comparison_page else 0,
                "product_b_name": state.product_b_data.get("name") if hasattr(state, 'product_b_data') else None,
                "output_files": [
                    str(faq_path.relative_to(Path.cwd())),
                    str(product_path.relative_to(Path.cwd())),
                    str(comparison_path.relative_to(Path.cwd()))
                ]
            }
        }
        
        # Write summary
        summary_path = output_dir / "execution_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return {
            "files_written": 4,
            "file_paths": [
                str(faq_path),
                str(product_path),
                str(comparison_path),
                str(summary_path)
            ],
            "file_sizes": {
                "faq.json": faq_path.stat().st_size,
                "product_page.json": product_path.stat().st_size,
                "comparison_page.json": comparison_path.stat().st_size
            }
        }
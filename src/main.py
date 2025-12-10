#!/usr/bin/env python3
"""
Main entry point for the Multi-Agent Content Generation System
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from src.agents.orchestrator import OrchestratorAgent
from src.core.state import state_manager


async def main():
    """Main execution function"""
    print("=" * 60)
    print("Multi-Agent Content Generation System")
    print("Kasparro Applied AI Engineer Challenge")
    print("=" * 60)
    
    # Input product data (from assignment)
    raw_product_data = {
        "name": "GlowBoost Vitamin C Serum",
        "concentration": "10% Vitamin C",
        "skin_type": ["Oily", "Combination"],
        "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
        "benefits": ["Brightening", "Fades dark spots"],
        "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "price": "₹699"
    }
    
    print("\n📦 Input Product Data:")
    print(json.dumps(raw_product_data, indent=2))
    
    # Create orchestrator
    orchestrator = OrchestratorAgent()
    
    print("\n📋 Execution Plan:")
    plan = orchestrator.get_execution_plan()
    print(f"Total Agents: {plan['total_agents']}")
    print(f"Execution Order: {' → '.join(plan['execution_order'])}")
    
    print("\n🚀 Starting Pipeline Execution...")
    print("-" * 40)
    
    start_time = datetime.now()
    
    try:
        # Execute pipeline
        result = await orchestrator.execute({
            "raw_product_data": raw_product_data
        })
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("✅ PIPELINE EXECUTION COMPLETE")
        print("=" * 60)
        
        print(f"\n📊 Execution Summary:")
        print(f"  Total Time: {execution_time:.2f} seconds")
        print(f"  Agents Executed: {result['data']['agents_executed']}")
        print(f"  Pipeline Success: {result['data']['pipeline_success']}")
        
        # Print state snapshot
        snapshot = result['data']['state_snapshot']
        print(f"\n📈 Final State Snapshot:")
        print(f"  Product: {snapshot['product']['name']}")
        print(f"  Questions Generated: {snapshot['questions_count']}")
        print(f"  Content Blocks: {len(snapshot['content_blocks'])}")
        print(f"  FAQ Items: {snapshot['faq_count']}")
        print(f"  Messages: {snapshot['message_count']}")
        print(f"  Errors: {snapshot['error_count']}")
        
        # List output files
        output_dir = Path("outputs")
        if output_dir.exists():
            print(f"\n💾 Output Files Generated:")
            for file in output_dir.glob("*.json"):
                print(f"  • {file.name}")
                
                # Show sample of each file
                with open(file, 'r') as f:
                    data = json.load(f)
                    print(f"    Size: {len(json.dumps(data))} bytes")
        
        # Save execution report
        report = {
            "execution_timestamp": start_time.isoformat(),
            "execution_duration_seconds": execution_time,
            "input_data": raw_product_data,
            "results": result['data']
        }
        
        report_path = Path("docs/execution_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
    except Exception as e:
        print(f"\n❌ Pipeline Execution Failed: {str(e)}")
        
        # Print error details from state
        state = state_manager.get_state()
        if state and state.errors:
            print("\n📝 Error Log:")
            for error in state.errors:
                print(f"  • {error}")
        
        raise
    
    print("\n" + "=" * 60)
    print("🎉 System Execution Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
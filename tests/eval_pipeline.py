import json
import time
import traceback
from typing import Dict, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

# Configure basic OpenTelemetry setup
provider = TracerProvider()
processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

from src.pipeline.graph import run_workflow

def load_dataset(path: str) -> list:
    with open(path, 'r') as f:
        return json.load(f)

def run_evaluation(dataset: list):
    results = {
        "total": len(dataset),
        "success": 0,
        "failed_execution": 0,
        "tool_selection_correct": 0,
        "accuracy_correct": 0,
        "average_latency": 0.0
    }
    
    total_latency = 0.0
    
    for i, item in enumerate(dataset):
        with tracer.start_as_current_span(f"eval_item_{i}") as span:
            span.set_attribute("question", item["question"])
            span.set_attribute("expected_tool", item["tool"])
            
            start_time = time.time()
            try:
                # We append a unique thread_id for each to avoid state pollution
                res = run_workflow(item["question"], thread_id=f"eval_{i}_{int(time.time())}")
                latency = time.time() - start_time
                total_latency += latency
                
                span.set_attribute("latency_sec", latency)
                
                # Check tool selection
                selected_tool = res.get("selected_tool")
                if isinstance(selected_tool, list) and item["tool"] in selected_tool:
                    results["tool_selection_correct"] += 1
                elif selected_tool == item["tool"]:
                    results["tool_selection_correct"] += 1
                
                # Check calculation accuracy
                calc_res = res.get("calculation_result", {})
                if calc_res:
                    # In this setup, calculation_result is usually a dict, e.g. {'force': 500}
                    # We will try to find a float value that matches our expected output
                    found_correct_value = False
                    
                    if item["type"] == "invalid":
                        # For invalid, we expect an exception or a specific validation warning
                        val_res = res.get("validation_result", {})
                        if not val_res.get("valid", True) or "error" in str(res).lower():
                            found_correct_value = True
                    else:
                        for k, v in calc_res.items():
                            if isinstance(v, (int, float)):
                                # Evaluate using validation_fn logic
                                expected = item["expected_result"]
                                if expected is not None:
                                    if abs(v - expected) < 0.1: # relaxed tolerance
                                        found_correct_value = True
                                        break

                    if found_correct_value:
                        results["accuracy_correct"] += 1
                        span.set_attribute("accuracy", "pass")
                    else:
                        span.set_attribute("accuracy", "fail")
                
                results["success"] += 1
            except Exception as e:
                latency = time.time() - start_time
                total_latency += latency
                span.set_attribute("latency_sec", latency)
                span.set_attribute("error", str(e))
                print(f"Error on item {i}: {e}")
                results["failed_execution"] += 1
    
    if results["total"] > 0:
        results["average_latency"] = total_latency / results["total"]
        
    return results

if __name__ == '__main__':
    print("Loading dataset...")
    dataset = load_dataset("tests/eval_data/dataset.json")
    print(f"Loaded {len(dataset)} items. Running evaluation on a subset of 10 items for speed...")
    
    subset = dataset[:5] + dataset[50:55] + dataset[100:105] + dataset[-5:] # mix of normal, edge, invalid
    subset = [x for x in subset if x] # filter out if out of bounds
    
    results = run_evaluation(subset)
    print("\n--- Evaluation Results ---")
    print(json.dumps(results, indent=2))
    
    # Save results
    with open("tests/eval_data/results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to tests/eval_data/results.json")

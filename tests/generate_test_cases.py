import json
import random

def generate_test_cases():
    test_cases = []
    
    # Generate Normal Cases
    for _ in range(50):
        mass = round(random.uniform(1.0, 100.0), 2)
        accel = round(random.uniform(1.0, 20.0), 2)
        expected = round(mass * accel, 4)
        test_cases.append({
            "question": f"Calculate the force for a mass of {mass} kg accelerating at {accel} m/s^2.",
            "tool": "calculate_force",
            "expected_result": expected,
            "type": "normal",
            "validation_fn": "lambda r: abs(r - {expected}) < 0.01".format(expected=expected)
        })
        
    for _ in range(50):
        force = round(random.uniform(10.0, 1000.0), 2)
        area = round(random.uniform(0.1, 10.0), 2)
        expected = round(force / area, 4)
        test_cases.append({
            "question": f"Find the normal stress if a force of {force} N is applied over an area of {area} m^2.",
            "tool": "calculate_stress",
            "expected_result": expected,
            "type": "normal",
            "validation_fn": "lambda r: abs(r - {expected}) < 0.01".format(expected=expected)
        })

    # Generate Edge Cases (very small or very large numbers)
    for _ in range(10):
        mass = 1e-5
        accel = 1e-5
        expected = mass * accel
        test_cases.append({
            "question": f"Calculate the force for a tiny mass of {mass} kg accelerating at {accel} m/s^2.",
            "tool": "calculate_force",
            "expected_result": expected,
            "type": "edge",
            "validation_fn": "lambda r: abs(r - {expected}) < 1e-8".format(expected=expected)
        })

    # Generate Invalid Inputs (e.g. division by zero for area)
    for _ in range(10):
        force = 500
        area = 0
        test_cases.append({
            "question": f"Find the normal stress if a force of {force} N is applied over an area of {area} m^2.",
            "tool": "calculate_stress",
            "expected_result": None,
            "type": "invalid",
            "validation_fn": "lambda r: r is None or 'error' in str(r).lower() or 'cannot be zero' in str(r).lower()"
        })

    with open('tests/eval_data/dataset.json', 'w') as f:
        json.dump(test_cases, f, indent=4)

if __name__ == '__main__':
    generate_test_cases()

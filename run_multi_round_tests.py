#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run multi-round pinyin tests where the program stays running
and accepts multiple input-search-select cycles.
"""

import json
import subprocess
import sys
import select
import os

def run_multi_round_tests(test_file, executable="./test_pinyin"):
    """Run multi-round tests from a JSON file."""
    
    # Load test cases
    with open(test_file, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    print(f"Running {len(test_cases)} multi-round test cases...\n")
    
    results = []
    passed = 0
    failed = 0
    
    for idx, test_case in enumerate(test_cases):
        print(f"Test {idx + 1}/{len(test_cases)}: {test_case['description']}")
        
        # Prepare all inputs upfront
        inputs = []
        for round_data in test_case['rounds']:
            # No prefix anymore - just pinyin
            inputs.append(round_data['pinyin'])
            for selection in round_data['selections']:
                inputs.append(str(selection['choice_index']))
        
        # Add EOF marker
        input_str = '\n'.join(inputs) + '\n'
        
        # Run the process
        try:
            result = subprocess.run(
                [executable],
                input=input_str,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout
            
            # Parse output to extract sentences
            sentences = []
            for line in output.split('\n'):
                if "sentence:" in line:
                    # Extract sentence after "sentence:" marker
                    sentence = line.split("sentence:", 1)[1].strip()
                    sentences.append(sentence)
            
            # Check if we got the right number of sentences (one per round)
            test_passed = True
            round_results = []
            
            if len(sentences) < len(test_case['rounds']):
                test_passed = False
                print(f"  ✗ FAILED: Expected {len(test_case['rounds'])} sentences, got {len(sentences)}")
                round_results.append({"error": f"Not enough sentences: {len(sentences)}/{len(test_case['rounds'])}"})
            else:
                # Check each round's expected result
                for round_idx, round_data in enumerate(test_case['rounds']):
                    expected = round_data['expected']
                    # Each round produces one final sentence
                    if round_idx < len(sentences):
                        actual = sentences[round_idx]
                        if actual == expected:
                            round_results.append({
                                "round": round_idx + 1,
                                "passed": True
                            })
                            print(f"  Round {round_idx + 1}: ✓ PASSED")
                        else:
                            test_passed = False
                            round_results.append({
                                "round": round_idx + 1,
                                "passed": False,
                                "expected": expected,
                                "actual": actual
                            })
                            print(f"  Round {round_idx + 1}: ✗ FAILED - expected '{expected}', got '{actual}'")
                    else:
                        test_passed = False
                        round_results.append({
                            "round": round_idx + 1,
                            "passed": False,
                            "error": "No sentence found"
                        })
                        print(f"  Round {round_idx + 1}: ✗ FAILED - no sentence")
            
        except subprocess.TimeoutExpired:
            test_passed = False
            print(f"  ✗ TIMEOUT")
            round_results.append({"error": "Timeout"})
        except Exception as e:
            test_passed = False
            print(f"  ✗ ERROR: {e}")
            round_results.append({"error": str(e)})
        
        if test_passed:
            passed += 1
            print(f"  Overall: ✓ PASSED\n")
        else:
            failed += 1
            print(f"  Overall: ✗ FAILED\n")
        
        results.append({
            "test_number": idx + 1,
            "description": test_case['description'],
            "passed": test_passed,
            "rounds": round_results
        })
    
    # Summary
    print("=" * 60)
    print(f"Total: {len(test_cases)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {100 * passed / len(test_cases):.1f}%")
    
    # Save results
    output_file = "multi_round_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to {output_file}")
    
    return failed == 0

if __name__ == "__main__":
    test_file = "multi_round_tests.json"
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    
    success = run_multi_round_tests(test_file)
    sys.exit(0 if success else 1)

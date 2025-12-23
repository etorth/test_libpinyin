#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run long sentence tests for libpinyin test_pinyin program
"""

import subprocess
import json
import time
import sys
from datetime import datetime

class LongTestRunner:
    def __init__(self, program_path="./test_pinyin", test_file="long_sentence_tests.json"):
        self.program_path = program_path
        self.test_file = test_file
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "total": 0,
            "too_long_but_worked": 0,
            "start_time": None,
            "end_time": None,
            "details": []
        }
    
    def load_test_cases(self):
        """Load test cases from JSON file"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_single_test(self, test_case):
        """Run a single test case"""
        test_id = test_case['id']
        prefix = test_case['prefix']
        pinyin = test_case['pinyin']
        expected = test_case.get('expected_contains')
        full_sentence = test_case.get('full_sentence', expected)
        description = test_case['description']
        
        # Prepare input: prefix + pinyin + select first candidate (0) + quit
        input_str = f"{prefix}\n{pinyin}\n0\nquit\n"
        
        try:
            # Run the program with timeout
            process = subprocess.Popen(
                [self.program_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            stdout, stderr = process.communicate(input=input_str, timeout=15)
            
            # Check results
            result = {
                "id": test_id,
                "description": description,
                "prefix": prefix,
                "pinyin": pinyin,
                "full_sentence": full_sentence,
                "expected": expected,
                "status": "unknown",
                "output": stdout,
                "error": stderr
            }
            
            # Check if sentence is too long (>15 chars)
            is_too_long = len(full_sentence) >= 16
            has_too_long_warning = "too long" in stdout
            
            # Check if expected phrase appears in output
            if expected in stdout:
                result["status"] = "passed"
                self.results["passed"] += 1
                
                # Track if it worked despite being too long
                if is_too_long and has_too_long_warning:
                    result["note"] = "Worked but not added to dictionary (too long)"
                    self.results["too_long_but_worked"] += 1
            else:
                result["status"] = "failed"
                result["reason"] = f"Expected '{expected}' not found in output"
                self.results["failed"] += 1
            
            self.results["details"].append(result)
            return result
            
        except subprocess.TimeoutExpired:
            process.kill()
            result = {
                "id": test_id,
                "description": description,
                "prefix": prefix,
                "pinyin": pinyin,
                "full_sentence": full_sentence,
                "status": "error",
                "reason": "Timeout (>15s)"
            }
            self.results["errors"] += 1
            self.results["details"].append(result)
            return result
            
        except Exception as e:
            result = {
                "id": test_id,
                "description": description,
                "prefix": prefix,
                "pinyin": pinyin,
                "full_sentence": full_sentence,
                "status": "error",
                "reason": str(e)
            }
            self.results["errors"] += 1
            self.results["details"].append(result)
            return result
    
    def run_all_tests(self):
        """Run all test cases"""
        test_cases = self.load_test_cases()
        self.results["total"] = len(test_cases)
        self.results["start_time"] = datetime.now().isoformat()
        
        print(f"Running {len(test_cases)} long sentence test cases...")
        print("=" * 70)
        
        for i, test_case in enumerate(test_cases, 1):
            result = self.run_single_test(test_case)
            
            # Print progress
            status_symbol = {
                "passed": "✓",
                "failed": "✗",
                "error": "E"
            }.get(result["status"], "?")
            
            # Truncate description for display
            desc_display = result['description'][:50]
            print(f"[{i:3d}/{len(test_cases)}] {status_symbol} Test #{result['id']}: {desc_display}")
            
            # Print details for failures
            if result["status"] == "failed":
                print(f"         Reason: {result.get('reason', 'Unknown')}")
            elif result["status"] == "passed" and result.get("note"):
                print(f"         Note: {result['note']}")
            
            # Small delay
            time.sleep(0.05)
        
        self.results["end_time"] = datetime.now().isoformat()
        
        # Print summary
        print("=" * 70)
        print("\nLong Sentence Test Summary:")
        print(f"  Total:   {self.results['total']}")
        print(f"  Passed:  {self.results['passed']} ({self.results['passed']/self.results['total']*100:.1f}%)")
        print(f"  Failed:  {self.results['failed']} ({self.results['failed']/self.results['total']*100:.1f}%)")
        print(f"  Errors:  {self.results['errors']} ({self.results['errors']/self.results['total']*100:.1f}%)")
        print(f"\n  Worked but too long for dictionary: {self.results['too_long_but_worked']}")
        
        # Calculate duration
        start = datetime.fromisoformat(self.results["start_time"])
        end = datetime.fromisoformat(self.results["end_time"])
        duration = (end - start).total_seconds()
        print(f"  Duration: {duration:.2f} seconds")
        
        return self.results
    
    def save_results(self, filename="long_test_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\nDetailed results saved to {filename}")
    
    def print_failures(self):
        """Print detailed information about failures"""
        failures = [d for d in self.results["details"] if d["status"] != "passed"]
        
        if not failures:
            print("\n🎉 All long sentence tests passed!")
            return
        
        print(f"\n{'=' * 70}")
        print(f"Failed/Error Tests ({len(failures)}):")
        print(f"{'=' * 70}")
        
        for i, fail in enumerate(failures, 1):
            print(f"\n[{i}] Test #{fail['id']}: {fail['description']}")
            print(f"    Status: {fail['status']}")
            print(f"    Sentence: {fail['full_sentence']}")
            print(f"    Pinyin: {fail['pinyin']}")
            print(f"    Reason: {fail.get('reason', 'Unknown')}")
            
            if fail.get('output'):
                # Find the actual sentence generated
                lines = fail['output'].strip().split('\n')
                for line in lines:
                    if 'sentence:' in line:
                        print(f"    Got: {line}")
                        break

if __name__ == "__main__":
    # Check if program exists
    import os
    if not os.path.exists("./test_pinyin"):
        print("Error: test_pinyin program not found!")
        print("Please run 'make' first to build the program.")
        sys.exit(1)
    
    # Check if test cases exist
    if not os.path.exists("long_sentence_tests.json"):
        print("Generating long sentence test cases...")
        subprocess.run(["python3", "generate_long_tests.py"])
    
    # Run tests
    runner = LongTestRunner()
    results = runner.run_all_tests()
    runner.save_results()
    runner.print_failures()
    
    # Exit with appropriate code
    if results["failed"] > 0 or results["errors"] > 0:
        sys.exit(1)
    else:
        print("\n✅ All long sentence tests passed!")
        sys.exit(0)

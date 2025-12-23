#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run multi-selection tests for libpinyin test_pinyin program
Simulates real user behavior with multiple candidate selections
"""

import subprocess
import json
import time
import sys
from datetime import datetime

class MultiSelectionTestRunner:
    def __init__(self, program_path="./test_pinyin", test_file="multi_selection_tests.json"):
        self.program_path = program_path
        self.test_file = test_file
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "total": 0,
            "start_time": None,
            "end_time": None,
            "details": []
        }
    
    def load_test_cases(self):
        """Load test cases from JSON file"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_single_test(self, test_case):
        """Run a single multi-selection test case"""
        test_id = test_case['id']
        prefix = test_case['prefix']
        pinyin = test_case['pinyin']
        selections = test_case['selections']
        final_sentence = test_case['final_sentence']
        description = test_case['description']
        
        # Build input: prefix + pinyin + multiple selections + quit
        input_lines = [prefix, pinyin]
        for selection in selections:
            input_lines.append(str(selection['index']))
        input_lines.append('quit')
        input_str = '\n'.join(input_lines) + '\n'
        
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
            
            stdout, stderr = process.communicate(input=input_str, timeout=20)
            
            # Parse output to check each selection
            result = {
                "id": test_id,
                "description": description,
                "prefix": prefix,
                "pinyin": pinyin,
                "selections": selections,
                "final_sentence": final_sentence,
                "status": "unknown",
                "output": stdout,
                "error": stderr,
                "selection_results": []
            }
            
            # Extract sentence outputs
            lines = stdout.split('\n')
            sentence_lines = [line for line in lines if 'sentence:' in line]
            
            # Check each selection result
            all_selections_passed = True
            for i, (selection, sentence_line) in enumerate(zip(selections, sentence_lines)):
                expected = selection['expected_contains']
                found = expected in sentence_line
                
                result["selection_results"].append({
                    "step": i + 1,
                    "expected": expected,
                    "found": found,
                    "actual": sentence_line.replace('sentence:', '').strip() if 'sentence:' in sentence_line else ""
                })
                
                if not found:
                    all_selections_passed = False
            
            # Overall result
            if all_selections_passed and len(sentence_lines) >= len(selections):
                result["status"] = "passed"
                self.results["passed"] += 1
                
                # Check if final sentence is too long
                if "too long" in stdout:
                    result["note"] = f"Final sentence too long ({len(final_sentence)} chars)"
            else:
                result["status"] = "failed"
                if len(sentence_lines) < len(selections):
                    result["reason"] = f"Expected {len(selections)} selections, got {len(sentence_lines)}"
                else:
                    failed_steps = [r["step"] for r in result["selection_results"] if not r["found"]]
                    result["reason"] = f"Selection step(s) {failed_steps} failed"
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
                "selections": selections,
                "final_sentence": final_sentence,
                "status": "error",
                "reason": "Timeout (>20s)"
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
                "selections": selections,
                "final_sentence": final_sentence,
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
        
        print(f"Running {len(test_cases)} multi-selection test cases...")
        print("=" * 80)
        
        for i, test_case in enumerate(test_cases, 1):
            result = self.run_single_test(test_case)
            
            # Print progress
            status_symbol = {
                "passed": "✓",
                "failed": "✗",
                "error": "E"
            }.get(result["status"], "?")
            
            # Truncate description for display
            desc_display = result['description'][:55]
            steps = len(result.get('selections', []))
            print(f"[{i:2d}/{len(test_cases)}] {status_symbol} Test #{result['id']}: {desc_display} ({steps} steps)")
            
            # Print details for failures
            if result["status"] == "failed":
                print(f"        Reason: {result.get('reason', 'Unknown')}")
                # Show which steps failed
                if 'selection_results' in result:
                    for sr in result['selection_results']:
                        if not sr['found']:
                            print(f"        Step {sr['step']}: Expected '{sr['expected']}', got '{sr['actual']}'")
            elif result["status"] == "passed" and result.get("note"):
                print(f"        Note: {result['note']}")
            
            # Small delay
            time.sleep(0.05)
        
        self.results["end_time"] = datetime.now().isoformat()
        
        # Print summary
        print("=" * 80)
        print("\nMulti-Selection Test Summary:")
        print(f"  Total:   {self.results['total']}")
        print(f"  Passed:  {self.results['passed']} ({self.results['passed']/self.results['total']*100:.1f}%)")
        print(f"  Failed:  {self.results['failed']} ({self.results['failed']/self.results['total']*100:.1f}%)")
        print(f"  Errors:  {self.results['errors']} ({self.results['errors']/self.results['total']*100:.1f}%)")
        
        # Calculate duration
        start = datetime.fromisoformat(self.results["start_time"])
        end = datetime.fromisoformat(self.results["end_time"])
        duration = (end - start).total_seconds()
        print(f"  Duration: {duration:.2f} seconds")
        
        return self.results
    
    def save_results(self, filename="multi_selection_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\nDetailed results saved to {filename}")
    
    def print_failures(self):
        """Print detailed information about failures"""
        failures = [d for d in self.results["details"] if d["status"] != "passed"]
        
        if not failures:
            print("\n🎉 All multi-selection tests passed!")
            return
        
        print(f"\n{'=' * 80}")
        print(f"Failed/Error Tests ({len(failures)}):")
        print(f"{'=' * 80}")
        
        for i, fail in enumerate(failures, 1):
            print(f"\n[{i}] Test #{fail['id']}: {fail['description']}")
            print(f"    Status: {fail['status']}")
            print(f"    Final sentence: {fail['final_sentence']}")
            print(f"    Pinyin: {fail['pinyin']}")
            print(f"    Reason: {fail.get('reason', 'Unknown')}")
            
            if 'selection_results' in fail:
                print(f"    Selection details:")
                for sr in fail['selection_results']:
                    status = "✓" if sr['found'] else "✗"
                    print(f"      Step {sr['step']} {status}: Expected '{sr['expected']}'")
                    if not sr['found']:
                        print(f"                 Got: '{sr['actual']}'")
    
    def print_statistics(self):
        """Print detailed statistics"""
        if not self.results["details"]:
            return
        
        print(f"\n{'=' * 80}")
        print("Detailed Statistics:")
        print(f"{'=' * 80}")
        
        # Count by number of steps
        step_counts = {}
        for detail in self.results["details"]:
            num_steps = len(detail.get('selections', []))
            if num_steps not in step_counts:
                step_counts[num_steps] = {"passed": 0, "failed": 0, "total": 0}
            step_counts[num_steps]["total"] += 1
            if detail["status"] == "passed":
                step_counts[num_steps]["passed"] += 1
            else:
                step_counts[num_steps]["failed"] += 1
        
        print("\nBy number of selection steps:")
        for steps in sorted(step_counts.keys()):
            counts = step_counts[steps]
            pass_rate = counts["passed"] / counts["total"] * 100 if counts["total"] > 0 else 0
            print(f"  {steps}-step: {counts['passed']}/{counts['total']} passed ({pass_rate:.1f}%)")
        
        # Count with/without prefix
        with_prefix = [d for d in self.results["details"] if d.get('prefix')]
        without_prefix = [d for d in self.results["details"] if not d.get('prefix')]
        
        print(f"\nBy prefix usage:")
        if with_prefix:
            passed_with = len([d for d in with_prefix if d['status'] == 'passed'])
            print(f"  With prefix: {passed_with}/{len(with_prefix)} passed ({passed_with/len(with_prefix)*100:.1f}%)")
        if without_prefix:
            passed_without = len([d for d in without_prefix if d['status'] == 'passed'])
            print(f"  Without prefix: {passed_without}/{len(without_prefix)} passed ({passed_without/len(without_prefix)*100:.1f}%)")

if __name__ == "__main__":
    # Check if program exists
    import os
    if not os.path.exists("./test_pinyin"):
        print("Error: test_pinyin program not found!")
        print("Please run 'make' first to build the program.")
        sys.exit(1)
    
    # Check if test cases exist
    if not os.path.exists("multi_selection_tests.json"):
        print("Generating multi-selection test cases...")
        subprocess.run(["python3", "generate_multi_selection_tests.py"])
    
    # Run tests
    runner = MultiSelectionTestRunner()
    results = runner.run_all_tests()
    runner.save_results()
    runner.print_failures()
    runner.print_statistics()
    
    # Exit with appropriate code
    if results["failed"] > 0 or results["errors"] > 0:
        print(f"\n⚠️  {results['failed']} test(s) failed, {results['errors']} error(s)")
        sys.exit(1)
    else:
        print("\n✅ All multi-selection tests passed!")
        sys.exit(0)

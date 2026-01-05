#!/usr/bin/env python3
import json
import subprocess
import sys

def run_multi_round_test(test_case):
    """Run a single multi-round test case"""
    print(f"\n{'='*80}")
    print(f"Test: {test_case['description']}")
    print(f"{'='*80}")
    
    # Start test_pinyin process
    process = subprocess.Popen(
        ['./test_pinyin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    round_num = 0
    for round_data in test_case['rounds']:
        round_num += 1
        prefix = round_data['prefix']
        pinyin = round_data['pinyin']
        expected = round_data['expected']
        
        print(f"\nRound {round_num}: prefix='{prefix}', pinyin='{pinyin}', expected='{expected}'")
        
        try:
            # Send prefix
            process.stdin.write(prefix + '\n')
            process.stdin.flush()
            
            # Send pinyin
            process.stdin.write(pinyin + '\n')
            process.stdin.flush()
            
            # Read candidates output
            output_lines = []
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                output_lines.append(line.strip())
                
                # Look for "choose:" prompt
                if line.strip().startswith('choose:'):
                    break
            
            # Find the expected candidate
            candidate_found = False
            candidate_index = -1
            
            for line in output_lines:
                # Parse candidate line like "0:你把(1) 1:你爸(1) ..."
                if ':' in line and '(' in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part and '(' in part:
                            idx_text = part.split(':')
                            if len(idx_text) == 2:
                                idx = idx_text[0]
                                text_with_score = idx_text[1]
                                text = text_with_score.split('(')[0]
                                
                                if text == expected:
                                    candidate_found = True
                                    candidate_index = int(idx)
                                    break
                    if candidate_found:
                        break
            
            if not candidate_found:
                print(f"  ❌ FAILED: Expected '{expected}' not found in candidates")
                print(f"  Candidates output:")
                for line in output_lines:
                    print(f"    {line}")
                process.kill()
                return False
            
            # Send selection
            process.stdin.write(str(candidate_index) + '\n')
            process.stdin.flush()
            
            # Read until next prompt
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                if 'prefix (Chinese chars):' in line:
                    break
            
            print(f"  ✓ Round {round_num} passed")
            
        except Exception as e:
            print(f"  ❌ FAILED with exception: {e}")
            process.kill()
            return False
    
    # Cleanup
    process.stdin.close()
    process.terminate()
    process.wait(timeout=2)
    
    print(f"\n✓ All {round_num} rounds passed for this test")
    return True

def main():
    # Clean build
    print("Cleaning and rebuilding...")
    subprocess.run(['make', 'clean'], check=True)
    subprocess.run(['make'], check=True)
    
    # Load test cases
    with open('multi_round_tests.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    print(f"\nRunning {len(test_cases)} multi-round tests...")
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        if run_multi_round_test(test_case):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"{'='*80}")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())

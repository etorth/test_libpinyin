# Test Suite Quick Reference

## Running Tests

### Run all 200 tests
```bash
python3 run_tests.py
```

### Generate new test cases
```bash
python3 generate_tests.py
```

### Run a quick subset test (first 20)
```bash
python3 << 'EOF'
import json
with open('test_cases.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)[:20]
with open('test_cases_quick.json', 'w', encoding='utf-8') as f:
    json.dump(cases, f, ensure_ascii=False, indent=2)
EOF

# Then modify run_tests.py to use test_cases_quick.json
```

## Test Structure

### Test Categories
- **1-50**: Basic phrases (no prefix)
- **51-100**: Context-based (with prefix)
- **101-120**: Long phrases
- **121-150**: Repeated inputs (learning test)
- **151-170**: Edge cases
- **171-200**: Mixed complexity

### Test Case Format
```json
{
  "id": 1,
  "prefix": "",
  "pinyin": "nihao",
  "expected_contains": "你好",
  "description": "Basic: 你好"
}
```

## Understanding Results

### Status Codes
- ✓ **passed**: Expected output found
- ✗ **failed**: Expected output not found
- E **error**: Timeout or crash

### Result Files
- `test_results.json`: Full detailed results
- `TEST_REPORT.md`: Human-readable summary

## Common Issues

### 1. Program Not Found
```bash
make  # Build test_pinyin first
```

### 2. Timeout Issues
Edit `run_tests.py`, line 53:
```python
stdout, stderr = process.communicate(input=input_str, timeout=10)
# Increase timeout to 30 for slower systems
```

### 3. Check Specific Test
```bash
# View test case #3
python3 -c "import json; cases=json.load(open('test_cases.json')); print(cases[2])"

# View result for test #3
python3 -c "import json; r=json.load(open('test_results.json')); print([d for d in r['details'] if d['id']==3][0])"
```

## Customizing Tests

### Add Your Own Phrases
Edit `generate_tests.py`, add to `test_data`:
```python
test_data = [
    # Your custom phrases
    ("你的短语", "nideduanyu"),
    # ... existing phrases
]
```

### Change Number of Tests
```python
# In generate_tests.py, line 282
test_cases = generate_test_cases(200)  # Change to desired number
```

## Performance Benchmarks

Typical performance on modern hardware:
- **Speed**: ~8 tests/second
- **200 tests**: ~24 seconds
- **Memory**: <100MB

## Automated CI Integration

### GitHub Actions Example
```yaml
- name: Run libpinyin tests
  run: |
    cd test_libpinyin
    make
    python3 run_tests.py
```

### Exit Codes
- `0`: All tests passed
- `1`: Some tests failed or errors occurred

## Debugging Failed Tests

### View full output of failed test
```python
import json
results = json.load(open('test_results.json'))
failed = [d for d in results['details'] if d['status'] == 'failed']
for f in failed:
    print(f"\n{'='*60}")
    print(f"Test #{f['id']}: {f['description']}")
    print(f"Output:\n{f['output']}")
```

### Manual test replication
```bash
./test_pinyin
# Type the prefix
# Type the pinyin
# Select candidate 0
# Type quit
```

## Tips

1. **First run is slower**: libpinyin loads dictionaries
2. **Repeated tests help**: System learns from selections
3. **Clean state**: Delete `data/user.conf` to reset learning
4. **Custom tests**: Modify test_data in generate_tests.py

## Support

For issues or questions:
1. Check TEST_REPORT.md for known issues
2. Review test_results.json for details
3. Run individual tests manually for debugging

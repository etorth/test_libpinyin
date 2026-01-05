#!/bin/bash

echo "Testing repeated input with same prefix and pinyin..."
echo ""

# Test 1: 我是 + niba (3 times)
echo "=== Test 1: prefix='我是', pinyin='niba' (3 rounds) ==="
(
echo "我是"
echo "niba"
echo "1"
echo "我是"
echo "niba"  
echo "1"
echo "我是"
echo "niba"
echo "1"
echo ""
echo ""
) | timeout 30 ./test_pinyin 2>&1 | head -100

echo ""
echo "=== Test completed without crash ==="

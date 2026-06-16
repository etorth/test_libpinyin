#!/bin/bash
set -e

echo "Testing repeated input with same prefix and pinyin..."
echo ""

PROGRAM=${TEST_PINYIN:-./install/test_pinyin}
if [ ! -x "$PROGRAM" ]; then
    echo "Error: $PROGRAM not found."
    echo "Please run './build.py' first to build the vcpkg/CMake test programs."
    exit 1
fi
PROGRAM_DIR=$(dirname "$PROGRAM")
PROGRAM_NAME=$(basename "$PROGRAM")

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
) | (cd "$PROGRAM_DIR" && timeout 30 "./$PROGRAM_NAME") 2>&1 | head -100

echo ""
echo "=== Test completed without crash ==="

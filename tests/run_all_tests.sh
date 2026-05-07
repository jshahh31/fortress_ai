#!/bin/bash
set -e

echo "Running Fortress AI test suite"
echo "================================"

echo "\nUnit tests"
pytest tests/unit/ -v --cov=app/services/document_parser

echo "\nIntegration tests"
pytest tests/integration/ -v

echo "\nPerformance benchmarks"
pytest tests/benchmark/ --benchmark-only

echo "\nAll tests passed"

#!/bin/bash
# Análise de Complexidade Ciclomática

echo "=== Análise de Complexidade Ciclomática ==="
echo ""

echo "Domain Layer:"
radon cc domain/ -a -s

echo ""
echo "Application Layer:"
radon cc application/ -a -s

echo ""
echo "Infrastructure Layer:"
radon cc infrastructure/ -a -s

echo ""
echo "=== Métodos com CC > 10 (CRÍTICO) ==="
radon cc domain/ application/ infrastructure/ -n C -s

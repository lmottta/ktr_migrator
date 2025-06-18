#!/bin/bash

echo "========================================"
echo "   KTR Migrator - Interface Web"
echo "========================================"
echo ""
echo "Iniciando interface web..."
echo "URL: http://localhost:8503"
echo ""
echo "Para parar: Pressione Ctrl+C"
echo ""

python -m streamlit run app.py --server.port=8503 --server.address=localhost --browser.gatherUsageStats=false 
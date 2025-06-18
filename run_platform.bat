@echo off
echo 🚀 Iniciando a KTR Platform Pro...
echo 📍 Acesse em seu navegador: http://localhost:8501
echo ⏹️  Para parar: Ctrl+C
echo --------------------------------------------------

echo 🔧 Verificando dependências...
pip install -r requirements_platform.txt --quiet

echo 🎯 Iniciando a plataforma...
streamlit run ktr_platform/app.py

pause 
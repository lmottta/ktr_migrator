#!/usr/bin/env python3
"""
Script para inicializar a Plataforma KTR
Central de Jobs e Schedules para migração de Pentaho KTR para Python
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Inicia a Plataforma KTR usando Streamlit"""
    
    # Verificar se o diretório da plataforma existe
    platform_dir = Path(__file__).parent / "ktr_platform"
    app_file = platform_dir / "app.py"
    
    if not app_file.exists():
        print("❌ Erro: Arquivo da aplicação não encontrado!")
        print(f"   Esperado em: {app_file}")
        return 1
    
    print("🚀 Iniciando a Plataforma KTR...")
    print("📍 Acesse em seu navegador: http://localhost:8501")
    print("⏹️  Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        # Executar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_file),
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n⏹️  Plataforma encerrada pelo usuário.")
        return 0
    except Exception as e:
        print(f"❌ Erro ao iniciar a plataforma: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
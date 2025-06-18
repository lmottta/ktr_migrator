#!/usr/bin/env python3
"""
Script para iniciar a interface web do KTR Migrator
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Inicia a interface Streamlit"""
    
    print("🚀 Iniciando KTR Migrator Web Interface...")
    print("📱 A interface será aberta no seu navegador automaticamente")
    print("🔗 URL: http://localhost:8501")
    print("💡 Para parar: Pressione Ctrl+C")
    print("-" * 50)
    
    # Caminho para o arquivo da interface
    interface_path = Path(__file__).parent / "interface.py"
    
    # Comando para executar Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(interface_path),
        "--server.port=8501",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false"
    ]
    
    try:
        # Executar Streamlit
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n✅ Interface encerrada!")
    except Exception as e:
        print(f"❌ Erro ao iniciar interface: {e}")

if __name__ == "__main__":
    main() 
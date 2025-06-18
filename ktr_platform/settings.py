from pathlib import Path

# Diretório base da plataforma
PLATFORM_DIR = Path(__file__).parent.resolve()

# Diretório para armazenar os projetos de fluxo gerados
FLOWS_DIR = PLATFORM_DIR / "flows"

# Diretório para armazenar dados da plataforma, como metadados de fluxos
DATA_DIR = PLATFORM_DIR / "data"

# Arquivo para armazenar os metadados dos fluxos
FLOWS_METADATA_FILE = DATA_DIR / "flows.json" 
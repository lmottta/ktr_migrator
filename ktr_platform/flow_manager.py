import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from settings import FLOWS_METADATA_FILE, FLOWS_DIR


@dataclass
class Flow:
    """Representa um fluxo de trabalho migrado."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Novo Fluxo"
    status: str = "Importando"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    project_path: Optional[str] = None
    last_run_at: Optional[str] = None
    
    # Novos campos para execução
    execution_status: str = "Nunca executado"
    execution_logs: List[str] = field(default_factory=list)
    execution_start_time: Optional[str] = None
    execution_end_time: Optional[str] = None
    execution_duration: Optional[float] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.project_path is None:
            self.project_path = str(FLOWS_DIR / self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "project_path": self.project_path,
            "last_run_at": self.last_run_at,
            "execution_status": self.execution_status,
            "execution_logs": self.execution_logs,
            "execution_start_time": self.execution_start_time,
            "execution_end_time": self.execution_end_time,
            "execution_duration": self.execution_duration,
            "error_message": self.error_message,
        }

    @staticmethod
    def from_dict(data: Dict):
        return Flow(**data)


class FlowManager:
    """Gerencia o ciclo de vida dos fluxos (CRUD) e a persistência."""

    def __init__(self):
        self._flows: Dict[str, Flow] = {}
        self._load_flows()

    def _load_flows(self):
        """Carrega os metadados dos fluxos do arquivo JSON."""
        if not FLOWS_METADATA_FILE.exists():
            self._save_flows()
            return

        with open(FLOWS_METADATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for flow_data in data:
                    flow = Flow.from_dict(flow_data)
                    self._flows[flow.id] = flow
            except json.JSONDecodeError:
                # O arquivo pode estar vazio ou corrompido, começamos com um estado limpo.
                pass

    def _save_flows(self):
        """Salva os metadados dos fluxos no arquivo JSON."""
        FLOWS_METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        flow_list = [flow.to_dict() for flow in self._flows.values()]
        with open(FLOWS_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(flow_list, f, indent=4, ensure_ascii=False)
            
    def get_all_flows(self) -> List[Flow]:
        """Retorna uma lista de todos os fluxos, ordenados por data de criação."""
        return sorted(list(self._flows.values()), key=lambda f: f.created_at, reverse=True)

    def add_flow(self, name: str) -> Flow:
        """Adiciona um novo fluxo."""
        new_flow = Flow(name=name)
        self._flows[new_flow.id] = new_flow
        self._save_flows()
        return new_flow

    def get_flow(self, flow_id: str) -> Optional[Flow]:
        """Busca um fluxo pelo seu ID."""
        return self._flows.get(flow_id)

    def update_flow_status(self, flow_id: str, status: str):
        """Atualiza o status de um fluxo."""
        flow = self.get_flow(flow_id)
        if flow:
            flow.status = status
            flow.updated_at = datetime.now().isoformat()
            self._save_flows()

    def update_execution_status(self, flow_id: str, execution_status: str, 
                               start_time: Optional[str] = None, 
                               end_time: Optional[str] = None,
                               duration: Optional[float] = None):
        """Atualiza o status de execução de um fluxo."""
        flow = self.get_flow(flow_id)
        if flow:
            flow.execution_status = execution_status
            flow.updated_at = datetime.now().isoformat()
            
            if start_time:
                flow.execution_start_time = start_time
            if end_time:
                flow.execution_end_time = end_time
                flow.last_run_at = end_time
            if duration:
                flow.execution_duration = duration
                
            self._save_flows()

    def update_execution_error(self, flow_id: str, error_message: str):
        """Armazena a mensagem de erro detalhada da execução, acumulando múltiplos erros."""
        flow = self.get_flow(flow_id)
        if flow:
            # Se já existe uma mensagem de erro, acumular em vez de sobrescrever
            if flow.error_message:
                # Evitar duplicações da mesma mensagem
                if error_message not in flow.error_message:
                    flow.error_message += f"\n\n---\n\n{error_message}"
            else:
                flow.error_message = error_message
            self._save_flows()

    def add_execution_log(self, flow_id: str, log_message: str):
        """Adiciona uma mensagem de log para a execução."""
        flow = self.get_flow(flow_id)
        if flow:
            timestamp = datetime.now().isoformat()
            flow.execution_logs.append(f"[{timestamp}] {log_message}")
            self._save_flows()

    def clear_execution_logs(self, flow_id: str):
        """Limpa os logs de execução e a mensagem de erro."""
        flow = self.get_flow(flow_id)
        if flow:
            flow.execution_logs = []
            flow.error_message = None
            self._save_flows()

    def delete_flow(self, flow_id: str):
        """Remove um fluxo."""
        if flow_id in self._flows:
            del self._flows[flow_id]
            self._save_flows()

    def rename_flow(self, flow_id: str, new_name: str):
        """Renomeia um fluxo."""
        flow = self.get_flow(flow_id)
        if flow:
            flow.name = new_name
            flow.updated_at = datetime.now().isoformat()
            self._save_flows() 
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
import sys
import os

from flow_manager import FlowManager


class FlowExecutor:
    """Executa fluxos Python de forma assíncrona e monitora sua execução."""
    
    def __init__(self, flow_manager: FlowManager):
        self.flow_manager = flow_manager
        self._running_processes = {}  # flow_id -> processo
        
    def execute_flow(self, flow_id: str, on_log: Optional[Callable[[str], None]] = None) -> bool:
        """
        Executa um fluxo de forma assíncrona.
        
        Args:
            flow_id: ID do fluxo a ser executado
            on_log: Callback opcional para receber logs em tempo real
            
        Returns:
            True se a execução foi iniciada com sucesso, False caso contrário
        """
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            return False
            
        if flow.status != "Pronto":
            return False
            
        if flow_id in self._running_processes:
            return False  # Já está executando
            
        # Limpar logs anteriores
        self.flow_manager.clear_execution_logs(flow_id)
        
        # Iniciar execução em thread separada
        thread = threading.Thread(
            target=self._run_flow_in_thread,
            args=(flow_id, on_log),
            daemon=True
        )
        thread.start()
        
        return True
    
    def _run_flow_in_thread(self, flow_id: str, on_log: Optional[Callable[[str], None]] = None):
        """Executa o fluxo em uma thread separada."""
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            return
            
        start_time = datetime.now()
        start_time_str = start_time.isoformat()
        
        try:
            # Atualizar status para "Executando"
            self.flow_manager.update_execution_status(
                flow_id, 
                "Executando",
                start_time=start_time_str
            )
            self._log_and_callback(flow_id, "🚀 Iniciando execução do fluxo...", on_log)
            
            # Encontrar o arquivo principal do pipeline
            project_path = Path(flow.project_path)
            pipeline_file = self._find_pipeline_file(project_path)
            
            if not pipeline_file:
                raise Exception("Arquivo de pipeline não encontrado")
                
            self._log_and_callback(flow_id, f"📁 Executando: {pipeline_file.name}", on_log)
            
            # Executar o pipeline
            process = subprocess.Popen(
                [sys.executable, str(pipeline_file)],
                cwd=str(project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self._running_processes[flow_id] = process
            
            # Capturar output em tempo real
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    self._log_and_callback(flow_id, line.strip(), on_log)
                    
            # Esperar processo terminar
            process.wait()
            
            # Remover da lista de processos rodando
            if flow_id in self._running_processes:
                del self._running_processes[flow_id]
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if process.returncode == 0:
                self.flow_manager.update_execution_status(
                    flow_id,
                    "Sucesso",
                    end_time=end_time.isoformat(),
                    duration=duration
                )
                self._log_and_callback(flow_id, f"✅ Execução concluída com sucesso em {duration:.2f}s", on_log)
            else:
                self.flow_manager.update_execution_status(
                    flow_id,
                    "Falha",
                    end_time=end_time.isoformat(),
                    duration=duration
                )
                self._log_and_callback(flow_id, f"❌ Execução falhou com código {process.returncode}", on_log)
                
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.flow_manager.update_execution_status(
                flow_id,
                "Erro",
                end_time=end_time.isoformat(),
                duration=duration
            )
            self._log_and_callback(flow_id, f"💥 Erro na execução: {str(e)}", on_log)
            
            # Remover da lista se estiver lá
            if flow_id in self._running_processes:
                del self._running_processes[flow_id]
    
    def _find_pipeline_file(self, project_path: Path) -> Optional[Path]:
        """Encontra o arquivo principal do pipeline."""
        # Procurar por arquivos Python na pasta src/pipelines/
        pipelines_dir = project_path / "src" / "pipelines"
        if pipelines_dir.exists():
            for file in pipelines_dir.glob("*.py"):
                if file.name != "__init__.py":
                    return file
                    
        # Fallback: procurar qualquer .py na raiz
        for file in project_path.glob("*.py"):
            if "pipeline" in file.name.lower():
                return file
                
        return None
    
    def _log_and_callback(self, flow_id: str, message: str, on_log: Optional[Callable[[str], None]]):
        """Adiciona log ao fluxo e chama callback se fornecido."""
        self.flow_manager.add_execution_log(flow_id, message)
        if on_log:
            on_log(message)
    
    def is_flow_running(self, flow_id: str) -> bool:
        """Verifica se um fluxo está executando."""
        return flow_id in self._running_processes
    
    def stop_flow(self, flow_id: str) -> bool:
        """Para a execução de um fluxo."""
        if flow_id not in self._running_processes:
            return False
            
        try:
            process = self._running_processes[flow_id]
            process.terminate()
            process.wait(timeout=5)  # Espera 5s para terminar graciosamente
        except subprocess.TimeoutExpired:
            process.kill()  # Força a parada se necessário
        finally:
            if flow_id in self._running_processes:
                del self._running_processes[flow_id]
            
            self.flow_manager.update_execution_status(
                flow_id,
                "Interrompido",
                end_time=datetime.now().isoformat()
            )
            self.flow_manager.add_execution_log(flow_id, "⏹️ Execução interrompida pelo usuário")
            
        return True
    
    def get_running_flows(self) -> list:
        """Retorna lista de IDs dos fluxos em execução."""
        return list(self._running_processes.keys()) 
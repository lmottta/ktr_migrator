import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, List
import sys
import os
import re

from flow_manager import FlowManager

def _stream_reader(stream, on_log: Callable[[str], None], stderr_lines: List[str], flow_id: str, flow_manager: FlowManager):
    """Lê um stream linha por linha, analisa erros em tempo real e chama o callback."""
    error_stage_patterns = {
        'extração': [
            r'❌ Erro na extração',
            r'FileNotFoundError',
            r'read_excel.*error',
            r'extraction.*failed',
            r'extract_data.*error'
        ],
        'transformação': [
            r'❌ Erro na transformação',
            r'transform_data.*error',
            r'KeyError.*column',
            r'transformation.*failed'
        ],
        'carregamento': [
            r'❌ Erro na carga',
            r'load_data.*error',
            r'database.*error',
            r'to_sql.*error',
            r'connection.*failed'
        ]
    }
    
    for line in iter(stream.readline, ''):
        if line:
            clean_line = line.strip()
            on_log(clean_line)
            
            # Capturar stderr separadamente
            if stderr_lines is not None:
                stderr_lines.append(clean_line)
            
            # Analisar se é um erro e identificar a etapa
            if any(keyword in clean_line.lower() for keyword in ['error', 'exception', 'traceback', 'failed']):
                stage = 'desconhecido'
                for stage_name, patterns in error_stage_patterns.items():
                    if any(re.search(pattern, clean_line, re.IGNORECASE) for pattern in patterns):
                        stage = stage_name
                        break
                
                # Salvar erro imediatamente com identificação da etapa
                error_msg = f"[{stage.upper()}] {clean_line}"
                flow_manager.update_execution_error(flow_id, error_msg)
                
    stream.close()

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
        """Executa o fluxo em uma thread separada, capturando stdout e stderr com análise em tempo real."""
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            return
            
        start_time = datetime.now()
        start_time_str = start_time.isoformat()
        
        try:
            self.flow_manager.update_execution_status(
                flow_id, 
                "Executando",
                start_time=start_time_str
            )
            self._log_and_callback(flow_id, "🚀 Iniciando execução do fluxo...", on_log)
            
            project_path = Path(flow.project_path)
            pipeline_file = self._find_pipeline_file(project_path)
            
            if not pipeline_file:
                raise FileNotFoundError("Arquivo de pipeline não encontrado")
                
            self._log_and_callback(flow_id, f"📁 Executando: {pipeline_file.name}", on_log)
            
            # Adicionar variáveis de ambiente para melhor rastreamento
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'  # Forçar output sem buffer
            env['PYTHONFAULTHANDLER'] = '1'  # Ativar handler de falhas
            
            process = subprocess.Popen(
                [sys.executable, str(pipeline_file)],
                cwd=str(project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,  # Sem buffer para captura em tempo real
                universal_newlines=True,
                env=env
            )
            
            self._running_processes[flow_id] = process
            
            stderr_output = []

            # Threads para capturar stdout e stderr em tempo real com análise
            stdout_thread = threading.Thread(
                target=_stream_reader,
                args=(
                    process.stdout, 
                    lambda line: self._log_and_callback(flow_id, line, on_log), 
                    None,
                    flow_id,
                    self.flow_manager
                ),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=_stream_reader,
                args=(
                    process.stderr, 
                    lambda line: self._log_and_callback(flow_id, f"[ERRO] {line}", on_log), 
                    stderr_output,
                    flow_id,
                    self.flow_manager
                ),
                daemon=True
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Monitorar processo em tempo real
            while process.poll() is None:
                time.sleep(0.5)  # Verificar a cada 500ms
                
                # Se já temos erro identificado, interromper
                current_flow = self.flow_manager.get_flow(flow_id)
                if current_flow and current_flow.error_message:
                    self._log_and_callback(flow_id, "💥 Erro detectado, interrompendo execução...", on_log)
                    process.terminate()
                    break

            # Esperar as threads de leitura finalizarem
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
            
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
                error_summary = f"❌ Execução falhou com código {process.returncode}"
                self.flow_manager.update_execution_status(
                    flow_id,
                    "Falha",
                    end_time=end_time.isoformat(),
                    duration=duration
                )
                self._log_and_callback(flow_id, error_summary, on_log)
                
                # Se não temos erro específico ainda, salvar o stderr completo
                current_flow = self.flow_manager.get_flow(flow_id)
                if not current_flow.error_message and stderr_output:
                    full_error_message = "\n".join(stderr_output)
                    self.flow_manager.update_execution_error(flow_id, f"[GERAL] {full_error_message}")

        except (Exception, FileNotFoundError) as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_message_str = f"💥 Erro inesperado na execução: {str(e)}"
            
            self.flow_manager.update_execution_status(
                flow_id,
                "Erro",
                end_time=end_time.isoformat(),
                duration=duration
            )
            self._log_and_callback(flow_id, error_message_str, on_log)
            self.flow_manager.update_execution_error(flow_id, f"[EXECUTOR] {str(e)}")
            
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
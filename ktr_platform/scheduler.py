"""
Sistema de Agendamento para KTR Platform
Gerencia execução automática de fluxos baseada em cronogramas definidos.
"""

import schedule
import threading
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from loguru import logger
import uuid

@dataclass
class ScheduleConfig:
    """Configuração de um agendamento."""
    id: str
    flow_id: str
    flow_name: str
    schedule_type: str  # 'daily', 'weekly', 'specific_dates', 'custom', 'interval'
    time: str = None  # formato HH:MM (para compatibilidade)
    times: List[str] = None  # múltiplos horários ['HH:MM', 'HH:MM']
    days: List[str] = None  # para weekly: ['monday', 'tuesday', ...]
    day_times: Dict[str, List[str]] = None  # horários específicos por dia {'monday': ['09:00', '15:00']}
    specific_dates: List[str] = None  # para specific_dates: ['2025-06-18', '2025-06-25', ...]
    specific_date_times: Dict[str, List[str]] = None  # horários por data específica
    start_date: str = None  # data de início para agendamentos
    end_date: str = None  # data de fim para agendamentos
    interval_minutes: int = None  # para execução a cada X minutos
    interval_start_time: str = None  # horário de início do intervalo
    interval_end_time: str = None  # horário de fim do intervalo
    active: bool = True
    created_at: str = None
    last_run: str = None
    next_run: str = None
    run_count: int = 0
    description: str = None  # descrição personalizada do agendamento

class FlowScheduler:
    """Gerenciador de agendamentos de fluxos."""
    
    def __init__(self, flow_manager, executor):
        self.flow_manager = flow_manager
        self.executor = executor
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.running = False
        self.thread = None
        self.data_file = "ktr_platform/data/schedules.json"
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Carregar agendamentos salvos
        self.load_schedules()
        
    def load_schedules(self):
        """Carrega agendamentos do arquivo JSON."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for schedule_data in data:
                        schedule = ScheduleConfig(**schedule_data)
                        self.schedules[schedule.id] = schedule
                logger.info(f"Carregados {len(self.schedules)} agendamentos")
        except Exception as e:
            logger.error(f"Erro ao carregar agendamentos: {e}")
    
    def save_schedules(self):
        """Salva agendamentos no arquivo JSON."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                data = [asdict(schedule) for schedule in self.schedules.values()]
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Agendamentos salvos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar agendamentos: {e}")
    
    def create_daily_schedule(self, flow_id: str, time: str) -> str:
        """Cria um agendamento diário."""
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            raise ValueError(f"Fluxo {flow_id} não encontrado")
        
        schedule_id = str(uuid.uuid4())
        schedule_config = ScheduleConfig(
            id=schedule_id,
            flow_id=flow_id,
            flow_name=flow.name,
            schedule_type='daily',
            time=time,
            created_at=datetime.now().isoformat()
        )
        
        self.schedules[schedule_id] = schedule_config
        self._register_schedule(schedule_config)
        self.save_schedules()
        
        logger.info(f"Agendamento diário criado: {flow.name} às {time}")
        return schedule_id
    
    def create_weekly_schedule(self, flow_id: str, days: List[str], time: str) -> str:
        """Cria um agendamento semanal."""
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            raise ValueError(f"Fluxo {flow_id} não encontrado")
        
        schedule_id = str(uuid.uuid4())
        schedule_config = ScheduleConfig(
            id=schedule_id,
            flow_id=flow_id,
            flow_name=flow.name,
            schedule_type='weekly',
            time=time,
            days=days,
            created_at=datetime.now().isoformat()
        )
        
        self.schedules[schedule_id] = schedule_config
        self._register_schedule(schedule_config)
        self.save_schedules()
        
        days_str = ", ".join(days)
        logger.info(f"Agendamento semanal criado: {flow.name} - {days_str} às {time}")
        return schedule_id
    
    def create_specific_dates_schedule(self, flow_id: str, dates: List[str], time: str, description: str = None) -> str:
        """Cria um agendamento para datas específicas."""
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            raise ValueError(f"Fluxo {flow_id} não encontrado")
        
        # Validar e ordenar datas
        try:
            date_objects = [datetime.fromisoformat(date) for date in dates]
            # Filtrar apenas datas futuras
            future_dates = [date.date().isoformat() for date in date_objects if date.date() >= datetime.now().date()]
            
            if not future_dates:
                raise ValueError("Todas as datas selecionadas já passaram")
                
        except ValueError as e:
            raise ValueError(f"Formato de data inválido: {e}")
        
        schedule_id = str(uuid.uuid4())
        schedule_config = ScheduleConfig(
            id=schedule_id,
            flow_id=flow_id,
            flow_name=flow.name,
            schedule_type='specific_dates',
            time=time,
            specific_dates=future_dates,
            description=description or f"Execução em {len(future_dates)} datas específicas",
            created_at=datetime.now().isoformat()
        )
        
        self.schedules[schedule_id] = schedule_config
        self._register_specific_dates_schedule(schedule_config)
        self.save_schedules()
        
        logger.info(f"Agendamento para datas específicas criado: {flow.name} - {len(future_dates)} datas")
        return schedule_id

    def create_custom_schedule(self, flow_id: str, time: str, start_date: str = None, end_date: str = None, 
                             days: List[str] = None, description: str = None) -> str:
        """Cria um agendamento customizado com período específico."""
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            raise ValueError(f"Fluxo {flow_id} não encontrado")
        
        schedule_id = str(uuid.uuid4())
        schedule_config = ScheduleConfig(
            id=schedule_id,
            flow_id=flow_id,
            flow_name=flow.name,
            schedule_type='custom',
            time=time,
            days=days,
            start_date=start_date,
            end_date=end_date,
            description=description or "Agendamento customizado",
            created_at=datetime.now().isoformat()
        )
        
        self.schedules[schedule_id] = schedule_config
        self._register_schedule(schedule_config)
        self.save_schedules()
        
        logger.info(f"Agendamento customizado criado: {flow.name}")
        return schedule_id

    def create_multiple_times_schedule(self, flow_id: str, times: List[str], schedule_type: str = 'daily', 
                                     days: List[str] = None, description: str = None) -> str:
        """Cria um agendamento com múltiplos horários."""
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            raise ValueError(f"Fluxo {flow_id} não encontrado")
        
        # Validar horários
        if not times or not all(self._validate_time_format(t) for t in times):
            raise ValueError("Formato de horário inválido. Use HH:MM")
        
        schedule_id = str(uuid.uuid4())
        schedule_config = ScheduleConfig(
            id=schedule_id,
            flow_id=flow_id,
            flow_name=flow.name,
            schedule_type=schedule_type,
            times=times,
            days=days,
            description=description or f"Múltiplos horários: {', '.join(times)}",
            created_at=datetime.now().isoformat()
        )
        
        self.schedules[schedule_id] = schedule_config
        self._register_multiple_times_schedule(schedule_config)
        self.save_schedules()
        
        logger.info(f"Agendamento múltiplos horários criado: {flow.name} - {len(times)} horários")
        return schedule_id

    def create_day_specific_times_schedule(self, flow_id: str, day_times: Dict[str, List[str]], 
                                         description: str = None) -> str:
        """Cria um agendamento com horários específicos por dia da semana."""
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            raise ValueError(f"Fluxo {flow_id} não encontrado")
        
        # Validar horários
        for day, times in day_times.items():
            if not times or not all(self._validate_time_format(t) for t in times):
                raise ValueError(f"Formato de horário inválido para {day}. Use HH:MM")
        
        schedule_id = str(uuid.uuid4())
        schedule_config = ScheduleConfig(
            id=schedule_id,
            flow_id=flow_id,
            flow_name=flow.name,
            schedule_type='weekly',
            day_times=day_times,
            description=description or "Horários específicos por dia",
            created_at=datetime.now().isoformat()
        )
        
        self.schedules[schedule_id] = schedule_config
        self._register_day_specific_times_schedule(schedule_config)
        self.save_schedules()
        
        total_executions = sum(len(times) for times in day_times.values())
        logger.info(f"Agendamento horários por dia criado: {flow.name} - {total_executions} execuções/semana")
        return schedule_id

    def create_interval_schedule(self, flow_id: str, interval_minutes: int, 
                               start_time: str = "00:00", end_time: str = "23:59",
                               days: List[str] = None, description: str = None) -> str:
        """Cria um agendamento com execução a intervalos regulares."""
        flow = self.flow_manager.get_flow(flow_id)
        if not flow:
            raise ValueError(f"Fluxo {flow_id} não encontrado")
        
        if interval_minutes < 1 or interval_minutes > 1440:  # 1 dia = 1440 minutos
            raise ValueError("Intervalo deve ser entre 1 e 1440 minutos")
        
        if not self._validate_time_format(start_time) or not self._validate_time_format(end_time):
            raise ValueError("Formato de horário inválido. Use HH:MM")
        
        schedule_id = str(uuid.uuid4())
        schedule_config = ScheduleConfig(
            id=schedule_id,
            flow_id=flow_id,
            flow_name=flow.name,
            schedule_type='interval',
            interval_minutes=interval_minutes,
            interval_start_time=start_time,
            interval_end_time=end_time,
            days=days,
            description=description or f"A cada {interval_minutes} minutos ({start_time}-{end_time})",
            created_at=datetime.now().isoformat()
        )
        
        self.schedules[schedule_id] = schedule_config
        self._register_interval_schedule(schedule_config)
        self.save_schedules()
        
        logger.info(f"Agendamento por intervalo criado: {flow.name} - {interval_minutes}min")
        return schedule_id

    def update_schedule(self, schedule_id: str, **kwargs) -> bool:
        """Atualiza um agendamento existente."""
        if schedule_id not in self.schedules:
            return False
        
        schedule_config = self.schedules[schedule_id]
        
        # Campos editáveis
        editable_fields = ['time', 'days', 'specific_dates', 'start_date', 'end_date', 'description']
        
        # Parar agendamento atual
        schedule.clear(schedule_id)
        
        # Atualizar campos
        for field, value in kwargs.items():
            if field in editable_fields and hasattr(schedule_config, field):
                setattr(schedule_config, field, value)
        
        # Recalcular próxima execução
        schedule_config.next_run = self._calculate_next_run(schedule_config)
        
        # Re-registrar agendamento
        if schedule_config.active:
            if schedule_config.schedule_type == 'specific_dates':
                self._register_specific_dates_schedule(schedule_config)
            else:
                self._register_schedule(schedule_config)
        
        self.save_schedules()
        logger.info(f"Agendamento atualizado: {schedule_config.flow_name}")
        return True
    
    def _register_schedule(self, schedule_config: ScheduleConfig):
        """Registra um agendamento no scheduler."""
        if not schedule_config.active:
            return
            
        def job():
            # Verificar se o agendamento ainda deve ser executado
            if not self._should_execute_now(schedule_config):
                return
            self._execute_scheduled_flow(schedule_config.id)
        
        if schedule_config.schedule_type == 'daily':
            schedule.every().day.at(schedule_config.time).do(job).tag(schedule_config.id)
        elif schedule_config.schedule_type == 'weekly':
            for day in schedule_config.days:
                getattr(schedule.every(), day.lower()).at(schedule_config.time).do(job).tag(schedule_config.id)
        elif schedule_config.schedule_type == 'custom':
            # Agendamento customizado considera período e dias
            if schedule_config.days:
                for day in schedule_config.days:
                    getattr(schedule.every(), day.lower()).at(schedule_config.time).do(job).tag(schedule_config.id)
            else:
                schedule.every().day.at(schedule_config.time).do(job).tag(schedule_config.id)

    def _should_execute_now(self, schedule_config: ScheduleConfig) -> bool:
        """Verifica se um agendamento deve ser executado agora."""
        now = datetime.now()
        
        # Verificar período para agendamentos customizados
        if schedule_config.schedule_type == 'custom':
            if schedule_config.start_date:
                start_date = datetime.fromisoformat(schedule_config.start_date)
                if now.date() < start_date.date():
                    return False
            
            if schedule_config.end_date:
                end_date = datetime.fromisoformat(schedule_config.end_date)
                if now.date() > end_date.date():
                    # Desativar agendamento expirado
                    schedule_config.active = False
                    self.save_schedules()
                    return False
        
        # Verificar datas específicas
        elif schedule_config.schedule_type == 'specific_dates':
            today = now.date().isoformat()
            if today not in schedule_config.specific_dates:
                return False
            
            # Remover data atual da lista após execução
            schedule_config.specific_dates.remove(today)
            if not schedule_config.specific_dates:
                # Desativar se não há mais datas
                schedule_config.active = False
            self.save_schedules()
        
        return True
    
    def _execute_scheduled_flow(self, schedule_id: str):
        """Executa um fluxo agendado."""
        try:
            schedule_config = self.schedules.get(schedule_id)
            if not schedule_config or not schedule_config.active:
                return
            
            logger.info(f"Executando fluxo agendado: {schedule_config.flow_name}")
            
            # Executar o fluxo
            success = self.executor.execute_flow(schedule_config.flow_id)
            
            # Atualizar estatísticas
            schedule_config.last_run = datetime.now().isoformat()
            schedule_config.run_count += 1
            
            # Calcular próxima execução
            schedule_config.next_run = self._calculate_next_run(schedule_config)
            
            self.save_schedules()
            
            if success:
                logger.info(f"Fluxo agendado executado com sucesso: {schedule_config.flow_name}")
            else:
                logger.error(f"Falha na execução do fluxo agendado: {schedule_config.flow_name}")
                
        except Exception as e:
            logger.error(f"Erro na execução agendada: {e}")
    
    def _calculate_next_run(self, schedule_config: ScheduleConfig) -> str:
        """Calcula a próxima execução do agendamento."""
        try:
            now = datetime.now()
            
            if schedule_config.schedule_type == 'interval':
                return self._calculate_next_interval_run(schedule_config, now)
            
            # Para agendamentos com múltiplos horários
            if schedule_config.times:
                return self._calculate_next_multiple_times_run(schedule_config, now)
            
            # Para agendamentos com horários específicos por dia
            if schedule_config.day_times:
                return self._calculate_next_day_specific_run(schedule_config, now)
            
            # Lógica original para horário único
            if schedule_config.time:
                time_parts = schedule_config.time.split(':')
                hour, minute = int(time_parts[0]), int(time_parts[1])
                
                if schedule_config.schedule_type == 'specific_dates':
                    if schedule_config.specific_dates:
                        # Próxima data específica
                        future_dates = []
                        for date_str in schedule_config.specific_dates:
                            try:
                                date_obj = datetime.fromisoformat(date_str)
                                target_datetime = date_obj.replace(hour=hour, minute=minute, second=0, microsecond=0)
                                if target_datetime >= now:
                                    future_dates.append(target_datetime)
                            except:
                                continue
                        
                        if future_dates:
                            return min(future_dates).isoformat()
                    return ""
                
                elif schedule_config.schedule_type == 'daily':
                    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if next_run <= now:
                        next_run += timedelta(days=1)
                    return next_run.isoformat()
                
                elif schedule_config.schedule_type in ['weekly', 'custom']:
                    # Para agendamentos customizados, verificar período
                    if schedule_config.schedule_type == 'custom':
                        if schedule_config.end_date:
                            end_date = datetime.fromisoformat(schedule_config.end_date)
                            if now.date() > end_date.date():
                                return ""  # Agendamento expirado
                    
                    # Encontrar o próximo dia da semana
                    weekdays = {
                        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                        'friday': 4, 'saturday': 5, 'sunday': 6
                    }
                    
                    days_to_check = schedule_config.days if schedule_config.days else ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    target_days = [weekdays[day.lower()] for day in days_to_check]
                    current_weekday = now.weekday()
                    
                    # Encontrar o próximo dia de execução
                    days_ahead = None
                    for target_day in sorted(target_days):
                        if target_day > current_weekday:
                            days_ahead = target_day - current_weekday
                            break
                        elif target_day == current_weekday:
                            # Mesmo dia - verificar se ainda não passou o horário
                            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                            if target_time > now:
                                days_ahead = 0
                                break
                    
                    if days_ahead is None:
                        # Próxima semana
                        days_ahead = (7 - current_weekday) + min(target_days)
                    
                    next_run = now + timedelta(days=days_ahead)
                    next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # Verificar se está dentro do período para agendamentos customizados
                    if schedule_config.schedule_type == 'custom':
                        if schedule_config.start_date:
                            start_date = datetime.fromisoformat(schedule_config.start_date)
                            if next_run.date() < start_date.date():
                                # Ajustar para a data de início
                                next_run = start_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                                # Encontrar o próximo dia válido a partir da data de início
                                while next_run.weekday() not in target_days:
                                    next_run += timedelta(days=1)
                        
                        if schedule_config.end_date:
                            end_date = datetime.fromisoformat(schedule_config.end_date)
                            if next_run.date() > end_date.date():
                                return ""  # Além do período
                    
                    return next_run.isoformat()
                    
        except Exception as e:
            logger.error(f"Erro ao calcular próxima execução: {e}")
            return ""

    def _calculate_next_interval_run(self, schedule_config: ScheduleConfig, now: datetime) -> str:
        """Calcula próxima execução para agendamentos por intervalo."""
        try:
            interval_minutes = schedule_config.interval_minutes
            start_time = datetime.strptime(schedule_config.interval_start_time, "%H:%M").time()
            end_time = datetime.strptime(schedule_config.interval_end_time, "%H:%M").time()
            
            # Calcular próxima execução
            next_run = now + timedelta(minutes=interval_minutes)
            
            # Ajustar para horário permitido
            if start_time <= end_time:
                # Mesmo dia
                if next_run.time() < start_time:
                    next_run = next_run.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
                elif next_run.time() > end_time:
                    # Próximo dia
                    next_run = next_run.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0) + timedelta(days=1)
            
            return next_run.isoformat()
        except:
            return ""

    def _calculate_next_multiple_times_run(self, schedule_config: ScheduleConfig, now: datetime) -> str:
        """Calcula próxima execução para múltiplos horários."""
        try:
            next_executions = []
            
            for time_str in schedule_config.times:
                time_parts = time_str.split(':')
                hour, minute = int(time_parts[0]), int(time_parts[1])
                
                if schedule_config.schedule_type == 'daily':
                    # Hoje
                    today_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if today_run > now:
                        next_executions.append(today_run)
                    
                    # Amanhã
                    tomorrow_run = today_run + timedelta(days=1)
                    next_executions.append(tomorrow_run)
                
                elif schedule_config.schedule_type == 'weekly' and schedule_config.days:
                    weekdays = {
                        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                        'friday': 4, 'saturday': 5, 'sunday': 6
                    }
                    
                    for day in schedule_config.days:
                        target_day = weekdays[day.lower()]
                        days_ahead = (target_day - now.weekday()) % 7
                        
                        if days_ahead == 0:  # Hoje
                            today_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                            if today_run > now:
                                next_executions.append(today_run)
                            else:
                                next_executions.append(today_run + timedelta(days=7))
                        else:
                            next_run = now + timedelta(days=days_ahead)
                            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
                            next_executions.append(next_run)
            
            if next_executions:
                return min(next_executions).isoformat()
            return ""
        except:
            return ""

    def _calculate_next_day_specific_run(self, schedule_config: ScheduleConfig, now: datetime) -> str:
        """Calcula próxima execução para horários específicos por dia."""
        try:
            next_executions = []
            weekdays = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }
            
            for day, times in schedule_config.day_times.items():
                target_day = weekdays[day.lower()]
                days_ahead = (target_day - now.weekday()) % 7
                
                for time_str in times:
                    time_parts = time_str.split(':')
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                    
                    if days_ahead == 0:  # Hoje
                        today_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        if today_run > now:
                            next_executions.append(today_run)
                        else:
                            next_executions.append(today_run + timedelta(days=7))
                    else:
                        next_run = now + timedelta(days=days_ahead)
                        next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        next_executions.append(next_run)
            
            if next_executions:
                return min(next_executions).isoformat()
            return ""
        except:
            return ""

    def delete_schedule(self, schedule_id: str) -> bool:
        """Remove um agendamento."""
        if schedule_id in self.schedules:
            # Remover do scheduler
            schedule.clear(schedule_id)
            
            # Remover da lista
            del self.schedules[schedule_id]
            self.save_schedules()
            
            logger.info(f"Agendamento removido: {schedule_id}")
            return True
        return False
    
    def toggle_schedule(self, schedule_id: str) -> bool:
        """Ativa/desativa um agendamento."""
        if schedule_id in self.schedules:
            schedule_config = self.schedules[schedule_id]
            schedule_config.active = not schedule_config.active
            
            if schedule_config.active:
                self._register_schedule(schedule_config)
            else:
                schedule.clear(schedule_id)
            
            self.save_schedules()
            logger.info(f"Agendamento {'ativado' if schedule_config.active else 'desativado'}: {schedule_config.flow_name}")
            return True
        return False
    
    def get_all_schedules(self) -> List[ScheduleConfig]:
        """Retorna todos os agendamentos."""
        # Atualizar próximas execuções
        for schedule_config in self.schedules.values():
            if schedule_config.active:
                schedule_config.next_run = self._calculate_next_run(schedule_config)
        
        return list(self.schedules.values())
    
    def get_next_runs(self, limit: int = 10) -> List[Dict]:
        """Retorna as próximas execuções agendadas."""
        next_runs = []
        
        for schedule_config in self.schedules.values():
            if schedule_config.active and schedule_config.next_run:
                try:
                    next_run_dt = datetime.fromisoformat(schedule_config.next_run)
                    next_runs.append({
                        'schedule_id': schedule_config.id,
                        'flow_name': schedule_config.flow_name,
                        'next_run': next_run_dt,
                        'next_run_str': next_run_dt.strftime('%d/%m/%Y %H:%M'),
                        'schedule_type': schedule_config.schedule_type,
                        'time': schedule_config.time,
                        'days': schedule_config.days
                    })
                except:
                    continue
        
        # Ordenar por próxima execução
        next_runs.sort(key=lambda x: x['next_run'])
        return next_runs[:limit]
    
    def start(self):
        """Inicia o scheduler em thread separada."""
        if self.running:
            return
        
        self.running = True
        
        # Registrar todos os agendamentos ativos
        schedule.clear()  # Limpar agendamentos anteriores
        for schedule_config in self.schedules.values():
            if schedule_config.active:
                self._register_schedule(schedule_config)
        
        # Iniciar thread do scheduler
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Scheduler iniciado")
    
    def stop(self):
        """Para o scheduler."""
        self.running = False
        schedule.clear()
        logger.info("Scheduler parado")
    
    def _run_scheduler(self):
        """Loop principal do scheduler."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Erro no scheduler: {e}")
                time.sleep(5)

    def _register_specific_dates_schedule(self, schedule_config: ScheduleConfig):
        """Registra agendamentos para datas específicas."""
        if not schedule_config.active or not schedule_config.specific_dates:
            return
            
        def job():
            self._execute_scheduled_flow(schedule_config.id)
        
        # Registrar para cada data específica
        for date_str in schedule_config.specific_dates:
            try:
                target_date = datetime.fromisoformat(date_str)
                # Apenas agendar se a data ainda não passou
                if target_date.date() >= datetime.now().date():
                    time_parts = schedule_config.time.split(':')
                    hour, minute = int(time_parts[0]), int(time_parts[1])
                    
                    # Agendar para a data e hora específicas
                    schedule.every().day.at(schedule_config.time).do(job).tag(schedule_config.id)
                    
            except Exception as e:
                logger.error(f"Erro ao registrar data específica {date_str}: {e}")

    def _register_multiple_times_schedule(self, schedule_config: ScheduleConfig):
        """Registra agendamento com múltiplos horários."""
        if not schedule_config.active or not schedule_config.times:
            return
            
        def create_job(time_str):
            def job():
                if not self._should_execute_now(schedule_config):
                    return
                self._execute_scheduled_flow(schedule_config.id)
            return job
        
        # Registrar para cada horário
        for time_str in schedule_config.times:
            if schedule_config.schedule_type == 'daily':
                schedule.every().day.at(time_str).do(create_job(time_str)).tag(schedule_config.id)
            elif schedule_config.schedule_type == 'weekly' and schedule_config.days:
                for day in schedule_config.days:
                    getattr(schedule.every(), day.lower()).at(time_str).do(create_job(time_str)).tag(schedule_config.id)

    def _register_day_specific_times_schedule(self, schedule_config: ScheduleConfig):
        """Registra agendamento com horários específicos por dia."""
        if not schedule_config.active or not schedule_config.day_times:
            return
            
        def create_job():
            def job():
                if not self._should_execute_now(schedule_config):
                    return
                self._execute_scheduled_flow(schedule_config.id)
            return job
        
        # Registrar para cada dia e horário
        for day, times in schedule_config.day_times.items():
            for time_str in times:
                getattr(schedule.every(), day.lower()).at(time_str).do(create_job()).tag(schedule_config.id)

    def _register_interval_schedule(self, schedule_config: ScheduleConfig):
        """Registra agendamento por intervalo."""
        if not schedule_config.active:
            return
        
        def job():
            # Verificar se está dentro do horário permitido
            now = datetime.now()
            current_time = now.time()
            
            start_time = datetime.strptime(schedule_config.interval_start_time, "%H:%M").time()
            end_time = datetime.strptime(schedule_config.interval_end_time, "%H:%M").time()
            
            # Verificar se está no horário permitido
            if start_time <= end_time:
                in_time_range = start_time <= current_time <= end_time
            else:  # Atravessa meia-noite
                in_time_range = current_time >= start_time or current_time <= end_time
            
            if not in_time_range:
                return
            
            # Verificar dia da semana se especificado
            if schedule_config.days:
                weekday_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                current_weekday = weekday_names[now.weekday()]
                if current_weekday.title() not in schedule_config.days:
                    return
            
            if not self._should_execute_now(schedule_config):
                return
                
            self._execute_scheduled_flow(schedule_config.id)
        
        # Registrar execução a cada intervalo
        schedule.every(schedule_config.interval_minutes).minutes.do(job).tag(schedule_config.id)

    def _validate_time_format(self, time_str: str) -> bool:
        """Valida formato de horário HH:MM."""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False 
"""
Experiment Tracker - ML experiment tracking and reproducibility
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from enum import Enum

class ExperimentStatus(Enum):
    """Experiment status"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ExperimentRun:
    """Individual experiment run"""
    run_id: str
    experiment_id: str
    name: str
    status: ExperimentStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    artifacts: List[str]
    logs: List[str]
    tags: List[str]
    notes: str
    git_commit: Optional[str]
    environment: Dict[str, str]
    seed: Optional[int]

@dataclass
class Experiment:
    """ML experiment definition"""
    experiment_id: str
    name: str
    description: str
    objective: str
    created_at: datetime
    created_by: str
    tags: List[str]
    total_runs: int
    best_run_id: Optional[str]
    best_metric_value: Optional[float]
    target_metric: str
    maximize_metric: bool

class ExperimentTracker:
    """ML experiment tracking and management"""
    
    def __init__(self, experiments_path: str = "ml_models/experiments"):
        self.experiments_path = Path(experiments_path)
        self.runs_path = self.experiments_path / "runs"
        self.artifacts_path = self.experiments_path / "artifacts"
        self.logs_path = self.experiments_path / "logs"
        self.db_path = self.experiments_path / "experiments.db"
        
        # Create directories
        self.experiments_path.mkdir(parents=True, exist_ok=True)
        self.runs_path.mkdir(exist_ok=True)
        self.artifacts_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Current run context
        self.current_run = None
    
    def _init_database(self):
        """Initialize SQLite database for experiment tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Experiments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                objective TEXT,
                created_at TIMESTAMP,
                created_by TEXT,
                tags TEXT,
                total_runs INTEGER DEFAULT 0,
                best_run_id TEXT,
                best_metric_value REAL,
                target_metric TEXT,
                maximize_metric BOOLEAN
            )
        ''')
        
        # Experiment runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiment_runs (
                run_id TEXT PRIMARY KEY,
                experiment_id TEXT,
                name TEXT,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds REAL,
                parameters TEXT,
                metrics TEXT,
                artifacts TEXT,
                logs TEXT,
                tags TEXT,
                notes TEXT,
                git_commit TEXT,
                environment TEXT,
                seed INTEGER,
                FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id)
            )
        ''')
        
        # Run metrics table (for time-series metrics)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_metrics (
                metric_id TEXT PRIMARY KEY,
                run_id TEXT,
                metric_name TEXT,
                metric_value REAL,
                step INTEGER,
                timestamp TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES experiment_runs (run_id)
            )
        ''')
        
        # Parameters table (for parameter search)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_parameters (
                param_id TEXT PRIMARY KEY,
                run_id TEXT,
                param_name TEXT,
                param_value TEXT,
                param_type TEXT,
                FOREIGN KEY (run_id) REFERENCES experiment_runs (run_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_experiment(self,
                         name: str,
                         description: str,
                         objective: str,
                         target_metric: str,
                         maximize_metric: bool = True,
                         created_by: str = "system",
                         tags: List[str] = None) -> Experiment:
        """Create a new experiment"""
        
        experiment_id = f"exp_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            objective=objective,
            created_at=datetime.now(),
            created_by=created_by,
            tags=tags or [],
            total_runs=0,
            best_run_id=None,
            best_metric_value=None,
            target_metric=target_metric,
            maximize_metric=maximize_metric
        )
        
        # Save to database
        self._save_experiment(experiment)
        
        print(f"🧪 Experiment created: {name} ({experiment_id})")
        return experiment
    
    def start_run(self,
                  experiment_id: str,
                  run_name: str = None,
                  parameters: Dict[str, Any] = None,
                  tags: List[str] = None,
                  notes: str = "",
                  seed: int = None) -> ExperimentRun:
        """Start a new experiment run"""
        
        if run_name is None:
            run_name = f"run_{int(time.time())}"
        
        run_id = f"run_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        # Get git commit if available
        git_commit = self._get_git_commit()
        
        # Get environment info
        environment = self._get_environment_info()
        
        run = ExperimentRun(
            run_id=run_id,
            experiment_id=experiment_id,
            name=run_name,
            status=ExperimentStatus.RUNNING,
            start_time=datetime.now(),
            end_time=None,
            duration_seconds=None,
            parameters=parameters or {},
            metrics={},
            artifacts=[],
            logs=[],
            tags=tags or [],
            notes=notes,
            git_commit=git_commit,
            environment=environment,
            seed=seed
        )
        
        # Save run
        self._save_run(run)
        
        # Set as current run
        self.current_run = run
        
        print(f"🏃 Run started: {run_name} ({run_id})")
        return run
    
    def log_parameter(self, key: str, value: Any, run_id: str = None):
        """Log a parameter for the current or specified run"""
        target_run_id = run_id or (self.current_run.run_id if self.current_run else None)
        
        if not target_run_id:
            raise ValueError("No active run. Start a run first or provide run_id.")
        
        # Update run parameters
        if self.current_run and self.current_run.run_id == target_run_id:
            self.current_run.parameters[key] = value
        
        # Save parameter to database
        self._save_parameter(target_run_id, key, value)
        
        print(f"📝 Parameter logged: {key} = {value}")
    
    def log_metric(self, key: str, value: float, step: int = None, run_id: str = None):
        """Log a metric for the current or specified run"""
        target_run_id = run_id or (self.current_run.run_id if self.current_run else None)
        
        if not target_run_id:
            raise ValueError("No active run. Start a run first or provide run_id.")
        
        # Update run metrics
        if self.current_run and self.current_run.run_id == target_run_id:
            self.current_run.metrics[key] = value
        
        # Save metric to database
        self._save_metric(target_run_id, key, value, step)
        
        print(f"📊 Metric logged: {key} = {value}")
    
    def log_artifact(self, artifact_path: str, run_id: str = None):
        """Log an artifact for the current or specified run"""
        target_run_id = run_id or (self.current_run.run_id if self.current_run else None)
        
        if not target_run_id:
            raise ValueError("No active run. Start a run first or provide run_id.")
        
        # Copy artifact to managed location
        source_path = Path(artifact_path)
        if source_path.exists():
            target_path = self.artifacts_path / target_run_id / source_path.name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            import shutil
            shutil.copy2(source_path, target_path)
            
            # Update run artifacts
            if self.current_run and self.current_run.run_id == target_run_id:
                self.current_run.artifacts.append(str(target_path))
            
            print(f"📎 Artifact logged: {source_path.name}")
        else:
            print(f"⚠️ Artifact not found: {artifact_path}")
    
    def log_text(self, text: str, run_id: str = None):
        """Log text/notes for the current or specified run"""
        target_run_id = run_id or (self.current_run.run_id if self.current_run else None)
        
        if not target_run_id:
            raise ValueError("No active run. Start a run first or provide run_id.")
        
        # Append to run logs
        log_entry = f"[{datetime.now().isoformat()}] {text}"
        
        if self.current_run and self.current_run.run_id == target_run_id:
            self.current_run.logs.append(log_entry)
        
        # Save to log file
        log_file = self.logs_path / f"{target_run_id}.log"
        with open(log_file, 'a') as f:
            f.write(log_entry + "\n")
        
        print(f"📝 Text logged: {text[:50]}...")
    
    def end_run(self, status: ExperimentStatus = ExperimentStatus.COMPLETED, run_id: str = None):
        """End the current or specified run"""
        target_run_id = run_id or (self.current_run.run_id if self.current_run else None)
        
        if not target_run_id:
            raise ValueError("No active run to end.")
        
        end_time = datetime.now()
        
        if self.current_run and self.current_run.run_id == target_run_id:
            self.current_run.status = status
            self.current_run.end_time = end_time
            self.current_run.duration_seconds = (end_time - self.current_run.start_time).total_seconds()
            
            # Update database
            self._update_run(self.current_run)
            
            # Update experiment best run if applicable
            self._update_best_run(self.current_run)
            
            print(f"🏁 Run ended: {self.current_run.name} ({status.value})")
            print(f"   Duration: {self.current_run.duration_seconds:.2f} seconds")
            
            # Clear current run
            self.current_run = None
    
    def get_experiment(self, experiment_id: str) -> Experiment:
        """Get experiment by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM experiments WHERE experiment_id = ?', (experiment_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        # Convert to Experiment object
        columns = [
            'experiment_id', 'name', 'description', 'objective', 'created_at',
            'created_by', 'tags', 'total_runs', 'best_run_id', 'best_metric_value',
            'target_metric', 'maximize_metric'
        ]
        data = dict(zip(columns, result))
        
        # Parse JSON fields
        data['tags'] = json.loads(data['tags']) if data['tags'] else []
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        return Experiment(**data)
    
    def get_run(self, run_id: str) -> ExperimentRun:
        """Get run by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM experiment_runs WHERE run_id = ?', (run_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise ValueError(f"Run not found: {run_id}")
        
        # Convert to ExperimentRun object
        columns = [
            'run_id', 'experiment_id', 'name', 'status', 'start_time', 'end_time',
            'duration_seconds', 'parameters', 'metrics', 'artifacts', 'logs',
            'tags', 'notes', 'git_commit', 'environment', 'seed'
        ]
        data = dict(zip(columns, result))
        
        # Parse JSON fields
        data['parameters'] = json.loads(data['parameters']) if data['parameters'] else {}
        data['metrics'] = json.loads(data['metrics']) if data['metrics'] else {}
        data['artifacts'] = json.loads(data['artifacts']) if data['artifacts'] else []
        data['logs'] = json.loads(data['logs']) if data['logs'] else []
        data['tags'] = json.loads(data['tags']) if data['tags'] else []
        data['environment'] = json.loads(data['environment']) if data['environment'] else {}
        
        # Parse datetime fields
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data['end_time']:
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        
        # Parse status
        data['status'] = ExperimentStatus(data['status'])
        
        return ExperimentRun(**data)
    
    def list_experiments(self) -> List[Experiment]:
        """List all experiments"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT experiment_id FROM experiments ORDER BY created_at DESC')
        experiment_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [self.get_experiment(exp_id) for exp_id in experiment_ids]
    
    def list_runs(self, experiment_id: str = None, limit: int = None) -> List[ExperimentRun]:
        """List runs for an experiment or all runs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if experiment_id:
            query = 'SELECT run_id FROM experiment_runs WHERE experiment_id = ? ORDER BY start_time DESC'
            params = (experiment_id,)
        else:
            query = 'SELECT run_id FROM experiment_runs ORDER BY start_time DESC'
            params = ()
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, params)
        run_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [self.get_run(run_id) for run_id in run_ids]
    
    def compare_runs(self, run_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple runs"""
        runs = [self.get_run(run_id) for run_id in run_ids]
        
        comparison = {
            'runs': {run.run_id: {
                'name': run.name,
                'status': run.status.value,
                'duration_seconds': run.duration_seconds,
                'parameters': run.parameters,
                'metrics': run.metrics
            } for run in runs},
            'parameter_differences': {},
            'metric_differences': {},
            'best_metrics': {}
        }
        
        # Find parameter differences
        all_params = set()
        for run in runs:
            all_params.update(run.parameters.keys())
        
        for param in all_params:
            values = {run.run_id: run.parameters.get(param) for run in runs}
            if len(set(str(v) for v in values.values())) > 1:  # Different values
                comparison['parameter_differences'][param] = values
        
        # Find metric differences and best values
        all_metrics = set()
        for run in runs:
            all_metrics.update(run.metrics.keys())
        
        for metric in all_metrics:
            values = {run.run_id: run.metrics.get(metric) for run in runs if run.metrics.get(metric) is not None}
            if len(values) > 1:
                comparison['metric_differences'][metric] = values
                # Find best value (assuming higher is better by default)
                best_run_id = max(values.keys(), key=lambda k: values[k])
                comparison['best_metrics'][metric] = {
                    'run_id': best_run_id,
                    'value': values[best_run_id]
                }
        
        return comparison
    
    def _save_experiment(self, experiment: Experiment):
        """Save experiment to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO experiments (
                experiment_id, name, description, objective, created_at, created_by,
                tags, total_runs, best_run_id, best_metric_value, target_metric, maximize_metric
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            experiment.experiment_id, experiment.name, experiment.description,
            experiment.objective, experiment.created_at, experiment.created_by,
            json.dumps(experiment.tags), experiment.total_runs, experiment.best_run_id,
            experiment.best_metric_value, experiment.target_metric, experiment.maximize_metric
        ))
        
        conn.commit()
        conn.close()
    
    def _save_run(self, run: ExperimentRun):
        """Save run to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO experiment_runs (
                run_id, experiment_id, name, status, start_time, end_time,
                duration_seconds, parameters, metrics, artifacts, logs, tags,
                notes, git_commit, environment, seed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            run.run_id, run.experiment_id, run.name, run.status.value,
            run.start_time, run.end_time, run.duration_seconds,
            json.dumps(run.parameters), json.dumps(run.metrics),
            json.dumps(run.artifacts), json.dumps(run.logs),
            json.dumps(run.tags), run.notes, run.git_commit,
            json.dumps(run.environment), run.seed
        ))
        
        conn.commit()
        conn.close()
    
    def _update_run(self, run: ExperimentRun):
        """Update existing run in database"""
        self._save_run(run)  # INSERT OR REPLACE handles updates
    
    def _save_parameter(self, run_id: str, param_name: str, param_value: Any):
        """Save parameter to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        param_id = f"{run_id}_{param_name}"
        param_type = type(param_value).__name__
        
        cursor.execute('''
            INSERT OR REPLACE INTO run_parameters (
                param_id, run_id, param_name, param_value, param_type
            ) VALUES (?, ?, ?, ?, ?)
        ''', (param_id, run_id, param_name, str(param_value), param_type))
        
        conn.commit()
        conn.close()
    
    def _save_metric(self, run_id: str, metric_name: str, metric_value: float, step: int = None):
        """Save metric to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metric_id = f"{run_id}_{metric_name}_{step or 0}_{int(time.time())}"
        
        cursor.execute('''
            INSERT INTO run_metrics (
                metric_id, run_id, metric_name, metric_value, step, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (metric_id, run_id, metric_name, metric_value, step or 0, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def _update_best_run(self, run: ExperimentRun):
        """Update best run for experiment if this run is better"""
        try:
            experiment = self.get_experiment(run.experiment_id)
            
            if experiment.target_metric in run.metrics:
                metric_value = run.metrics[experiment.target_metric]
                
                should_update = False
                if experiment.best_metric_value is None:
                    should_update = True
                elif experiment.maximize_metric and metric_value > experiment.best_metric_value:
                    should_update = True
                elif not experiment.maximize_metric and metric_value < experiment.best_metric_value:
                    should_update = True
                
                if should_update:
                    # Update experiment
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE experiments 
                        SET best_run_id = ?, best_metric_value = ?, total_runs = total_runs + 1
                        WHERE experiment_id = ?
                    ''', (run.run_id, metric_value, experiment.experiment_id))
                    
                    conn.commit()
                    conn.close()
                    
                    print(f"🏆 New best run: {run.name} ({experiment.target_metric}: {metric_value})")
        
        except Exception as e:
            print(f"⚠️ Failed to update best run: {e}")
    
    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit hash"""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def _get_environment_info(self) -> Dict[str, str]:
        """Get environment information"""
        import sys
        import platform
        
        return {
            'python_version': sys.version,
            'platform': platform.platform(),
            'hostname': platform.node(),
            'timestamp': datetime.now().isoformat()
        }

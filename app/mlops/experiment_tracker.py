"""
Experiment Tracker - ML experiment tracking and reproducibility
Minimal working version for Phase 2 MLOps integration
"""

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ExperimentStatus:
    "Experiment status"

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExperimentRun:
    "Individual experiment run"

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
    "ML experiment definition"

    experiment_id: str
    name: str
    description: str
    objective: str
    tags: List[str]
    created_at: datetime
    runs: List[ExperimentRun]
    status: str
    best_run_id: Optional[str]


class ExperimentTracker:
    "ML experiment tracking and management"

    def __init__(self, experiments_path: str = "ml_models/experiments"):
        """Initialize experiment tracker."""
        self.experiments_path = Path(experiments_path)
        self.experiments_path.mkdir(parents=True, exist_ok=True)

        self.runs_path = self.experiments_path / "runs"
        self.runs_path.mkdir(exist_ok=True)

        self.db_path = self.experiments_path / "experiments.db"
        self.current_run: Optional[ExperimentRun] = None

        self._init_database()

    def _init_database(self):
        "Initialize SQLite database for experiment tracking"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create experiments table
        cursor.execute()
            "
            CREATE TABLE IF NOT EXISTS experiments ()
                experiment_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                objective TEXT,
                tags TEXT,
                created_at TEXT,
                status TEXT,
                best_run_id TEXT
            )
        "
        )

        # Create runs table
        cursor.execute()
            "
            CREATE TABLE IF NOT EXISTS runs ()
                run_id TEXT PRIMARY KEY,
                experiment_id TEXT,
                name TEXT,
                status TEXT,
                start_time TEXT,
                end_time TEXT,
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
        "
        )

        conn.commit()
        conn.close()

    def create_experiment()
        self,
        name: str,
        description: str = "",
        objective: str = "minimize",
        tags: List[str] = None) -> Experiment:
        """Create a new experiment"""
        experiment_id = f"exp_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            objective=objective,
            tags=tags or [],
            created_at=datetime.now(timezone.utc),
            runs=[],
            status="active",
            best_run_id=None)

        self._save_experiment(experiment)
        return experiment

    def start_run(
        self,
        experiment_id: str,
        run_name: str = None,
        tags: List[str] = None,
        parameters: Dict[str, Any] = None,
        seed: int = None) -> ExperimentRun:
        "Start a new experiment run"
        if run_name is None:
            run_name = f"run_{int(time.time())}"

        run_id = f"run_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        run = ExperimentRun(
            run_id=run_id,
            experiment_id=experiment_id,
            name=run_name,
            status=ExperimentStatus.RUNNING,
            start_time=datetime.now(timezone.utc),
            end_time=None,
            duration_seconds=None,
            parameters=parameters or {},
            metrics={},
            artifacts=[],
            logs=[],
            tags=tags or [],
            notes="",
            git_commit=self._get_git_commit(),
            environment=self._get_environment_info(),
            seed=seed)

        self.current_run = run
        self._save_run(run)
        return run

    def log_parameter(self, key: str, value: Any, run_id: str = None):
        "Log a parameter for the current or specified run"
        target_run_id = run_id or (
            self.current_run.run_id if self.current_run else None
        )

        if not target_run_id:
            raise ValueError("No active run. Start a run first.")

        if self.current_run and self.current_run.run_id == target_run_id:
            self.current_run.parameters[key] = value

        self._save_parameter(target_run_id, key, value)

    def log_metric(self, key: str, value: float, step: int = None, run_id: str = None):
        "Log a metric for the current or specified run"
        target_run_id = run_id or (
            self.current_run.run_id if self.current_run else None
        )

        if not target_run_id:
            raise ValueError("No active run. Start a run first.")

        if self.current_run and self.current_run.run_id == target_run_id:
            self.current_run.metrics[key] = value

        self._save_metric(target_run_id, key, value, step)

    def end_run(
        self, status: ExperimentStatus = ExperimentStatus.COMPLETED, run_id: str = None
    ):
        "End the current or specified run"
        target_run_id = run_id or (
            self.current_run.run_id if self.current_run else None
        )

        if not target_run_id:
            raise ValueError("No active run to end.")

        if self.current_run and self.current_run.run_id == target_run_id:
            self.current_run.status = status
            self.current_run.end_time = datetime.now(timezone.utc)
            self.current_run.duration_seconds = (
                self.current_run.end_time - self.current_run.start_time
            ).total_seconds()

            self._update_run(self.current_run)
            self._update_best_run(self.current_run)
            self.current_run = None

    def get_experiment(self, experiment_id: str) -> Experiment:
        "Get experiment by ID"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            "SELECT * FROM experiments WHERE experiment_id = ?", (experiment_id)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Experiment {experiment_id} not found")

        return Experiment(
    experiment_id=row[0],
            name=row[1],
            description=row[2],
            objective=row[3],
            tags=json.loads(row[4]) if row[4] else [],
            created_at=datetime.fromisoformat(row[5]),
            runs=[],  # Load runs separately if needed
            status=row[6],
            best_run_id=row[7])

    def _save_experiment(self, experiment: Experiment):
        "Save experiment to database"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            "
            INSERT OR REPLACE INTO experiments 
            (experiment_id, name, description, objective, tags, created_at, status, best_run_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ",
            ()
                experiment.experiment_id,
                experiment.name,
                experiment.description,
                experiment.objective,
                json.dumps(experiment.tags),
                experiment.created_at.isoformat(),
                experiment.status,
                experiment.best_run_id))

        conn.commit()
        conn.close()

    def _save_run(self, run: ExperimentRun):
        "Save run to database"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            "
            INSERT OR REPLACE INTO runs 
            (run_id, experiment_id, name, status, start_time, end_time, duration_seconds,
             parameters, metrics, artifacts, logs, tags, notes, git_commit, environment, seed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ",
            ()
                run.run_id,
                run.experiment_id,
                run.name,
                run.status.value,
                run.start_time.isoformat(),
                run.end_time.isoformat() if run.end_time else None,
                run.duration_seconds,
                json.dumps(run.parameters),
                json.dumps(run.metrics),
                json.dumps(run.artifacts),
                json.dumps(run.logs),
                json.dumps(run.tags),
                run.notes,
                run.git_commit,
                json.dumps(run.environment),
                run.seed))

        conn.commit()
        conn.close()

    def _update_run(self, run: ExperimentRun):
        "Update existing run in database"
        self._save_run(run)  # INSERT OR REPLACE handles updates

    def _save_parameter(self, run_id: str, param_name: str, param_value: Any):
        "Save parameter to database"
        # In this minimal version, parameters are stored as JSON in the run record
        pass

    def _save_metric()
        self, run_id: str, metric_name: str, metric_value: float, step: int = None
    ):
        "Save metric to database"
        # In this minimal version, metrics are stored as JSON in the run record
        pass

    def _update_best_run(self, run: ExperimentRun):
        "Update best run for experiment if this run is better"
        # Simplified best run tracking for minimal version
        pass

    def _get_git_commit(self) -> Optional[str]:
        "Get current git commit hash"
        try:
            import subprocess

            result = subprocess.run
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd="."
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    def _get_environment_info(self) -> Dict[str, str]:
        "Get environment information"
        import platform
        import sys

        return {}
            "python_version": sys.version,
            "platform": platform.platform,
            "python_executable": sys.executable,
        }


# Global instance for easy access
experiment_tracker = ExperimentTracker()


def get_experiment_tracker() -> ExperimentTracker:
    """Get the global experiment tracker instance."""
    return experiment_tracker

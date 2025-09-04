"""
Production Deployment Automation
Phase 2C Week 2: Production Deployment - Automation
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import Environment, get_config, initialize_config
from .health_checks import health_monitor, quick_health_check
from .monitoring import initialize_monitoring, shutdown_monitoring
from .security import security_auditor

logger = logging.getLogger(__name__)


class DeploymentPhase(Enum):
    """Deployment phases"""

    PREPARATION = "preparation"
    VALIDATION = "validation"
    BACKUP = "backup"
    DEPLOYMENT = "deployment"
    VERIFICATION = "verification"
    ROLLBACK = "rollback"
    COMPLETION = "completion"


@dataclass
class DeploymentResult:
    """Deployment result data"""

    phase: DeploymentPhase
    success: bool
    message: str
    timestamp: datetime
    duration: float
    details: Dict[str, Any]


class DeploymentManager:
    """Manage production deployment process"""

    def __init__(self, environment: Environment = Environment.PRODUCTION):
        self.environment = environment
        self.config = None
        self.deployment_log = []
        self.start_time = None
        self.backup_dir = None

        # Deployment configuration
        self.deployment_config = {
            "backup_retention_days": 30,
            "health_check_timeout": 120,
            "rollback_timeout": 300,
            "verification_delay": 30,
        }

    async def deploy(self) -> Dict[str, Any]:
        """Execute full deployment process"""
        self.start_time = datetime.now()
        deployment_id = f"deploy_{int(time.time())}"

        logger.info(f"Starting deployment {deployment_id} for {self.environment.value}")

        try:
            # Phase 1: Preparation
            await self._execute_phase(
                DeploymentPhase.PREPARATION, self._prepare_deployment
            )

            # Phase 2: Validation
            await self._execute_phase(
                DeploymentPhase.VALIDATION, self._validate_environment
            )

            # Phase 3: Backup
            await self._execute_phase(DeploymentPhase.BACKUP, self._create_backup)

            # Phase 4: Deployment
            await self._execute_phase(
                DeploymentPhase.DEPLOYMENT, self._deploy_application
            )

            # Phase 5: Verification
            await self._execute_phase(
                DeploymentPhase.VERIFICATION, self._verify_deployment
            )

            # Phase 6: Completion
            await self._execute_phase(
                DeploymentPhase.COMPLETION, self._complete_deployment
            )

            deployment_summary = self._generate_deployment_summary(deployment_id, True)
            logger.info(f"Deployment {deployment_id} completed successfully")

            return deployment_summary

        except Exception as e:
            logger.error(f"Deployment {deployment_id} failed: {e}")

            # Attempt rollback
            try:
                await self._execute_phase(
                    DeploymentPhase.ROLLBACK, self._rollback_deployment
                )
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")

            deployment_summary = self._generate_deployment_summary(
                deployment_id, False, str(e)
            )
            return deployment_summary

    async def _execute_phase(self, phase: DeploymentPhase, phase_func):
        """Execute deployment phase with error handling"""
        phase_start = time.time()

        try:
            logger.info(f"Executing phase: {phase.value}")
            result = await phase_func()

            duration = time.time() - phase_start

            deployment_result = DeploymentResult(
                phase=phase,
                success=True,
                message=f"Phase {phase.value} completed successfully",
                timestamp=datetime.now(),
                duration=duration,
                details=result or {},
            )

            self.deployment_log.append(deployment_result)
            logger.info(f"Phase {phase.value} completed in {duration:.2f}s")

        except Exception as e:
            duration = time.time() - phase_start

            deployment_result = DeploymentResult(
                phase=phase,
                success=False,
                message=f"Phase {phase.value} failed: {str(e)}",
                timestamp=datetime.now(),
                duration=duration,
                details={"error": str(e)},
            )

            self.deployment_log.append(deployment_result)
            logger.error(f"Phase {phase.value} failed after {duration:.2f}s: {e}")
            raise

    async def _prepare_deployment(self) -> Dict[str, Any]:
        """Prepare deployment environment"""
        # Initialize configuration
        self.config = initialize_config(self.environment)

        # Validate configuration
        config_issues = self.config.validate_config()
        if config_issues:
            raise RuntimeError(f"Configuration validation failed: {config_issues}")

        # Create necessary directories
        directories = [
            Path(self.config.database.path).parent,
            Path(self.config.monitoring.log_file).parent,
            Path("logs"),
            Path("data"),
            Path("backups"),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Set up logging
        logging_config = self.config.get_logging_config()
        logging.config.dictConfig(logging_config)

        return {
            "config_validated": True,
            "directories_created": len(directories),
            "environment": self.environment.value,
        }

    async def _validate_environment(self) -> Dict[str, Any]:
        """Validate deployment environment"""
        validation_results = {
            "system_requirements": await self._check_system_requirements(),
            "dependencies": await self._check_dependencies(),
            "security_audit": security_auditor.run_security_audit(),
            "disk_space": await self._check_disk_space(),
        }

        # Check for critical issues
        critical_issues = []

        if not validation_results["system_requirements"]["sufficient"]:
            critical_issues.append("Insufficient system resources")

        if not validation_results["dependencies"]["all_available"]:
            critical_issues.append("Missing required dependencies")

        if validation_results["security_audit"]["score_percentage"] < 70:
            critical_issues.append("Security score below minimum threshold")

        if not validation_results["disk_space"]["sufficient"]:
            critical_issues.append("Insufficient disk space")

        if critical_issues:
            raise RuntimeError(f"Environment validation failed: {critical_issues}")

        return validation_results

    async def _create_backup(self) -> Dict[str, Any]:
        """Create deployment backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"backups/deployment_{timestamp}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup database
        db_path = Path(self.config.database.path)
        if db_path.exists():
            backup_db_path = self.backup_dir / f"database_{timestamp}.db"
            shutil.copy2(db_path, backup_db_path)

        # Backup configuration
        config_backup_path = self.backup_dir / "config.json"
        with open(config_backup_path, "w") as f:
            import json

            json.dump(self.config.to_dict(), f, indent=2)

        # Backup logs
        logs_backup_dir = self.backup_dir / "logs"
        logs_dir = Path("logs")
        if logs_dir.exists():
            shutil.copytree(logs_dir, logs_backup_dir, dirs_exist_ok=True)

        # Clean old backups
        self._cleanup_old_backups()

        return {
            "backup_directory": str(self.backup_dir),
            "database_backed_up": db_path.exists(),
            "config_backed_up": True,
            "logs_backed_up": logs_dir.exists(),
        }

    async def _deploy_application(self) -> Dict[str, Any]:
        """Deploy application components"""
        deployment_steps = []

        # Initialize performance features
        try:
            if self.config.performance.database_optimization:
                from app.performance.database_optimization import (
                    init_optimized_database,
                )

                init_optimized_database(
                    self.config.database.path, self.config.database.max_connections
                )
                deployment_steps.append("Database optimization initialized")
        except ImportError:
            deployment_steps.append("Database optimization not available")

        # Initialize monitoring
        if self.config.monitoring.enabled:
            email_config = None
            if self.config.monitoring.alert_email_enabled:
                email_config = {
                    "smtp_host": os.getenv("SMTP_HOST"),
                    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                    "username": os.getenv("SMTP_USERNAME"),
                    "password": os.getenv("SMTP_PASSWORD"),
                    "from_email": os.getenv("SMTP_FROM_EMAIL"),
                    "to_emails": self.config.monitoring.alert_emails,
                }

            initialize_monitoring(email_config)
            deployment_steps.append("Monitoring system initialized")

        # Initialize MLOps service
        try:
            from app.services.mlops_service import MLOpsService

            mlops_service = MLOpsService()
            deployment_steps.append("MLOps service initialized")
        except Exception as e:
            logger.warning(f"MLOps service initialization failed: {e}")
            deployment_steps.append(f"MLOps service failed: {e}")

        return {
            "deployment_steps": deployment_steps,
            "total_steps": len(deployment_steps),
        }

    async def _verify_deployment(self) -> Dict[str, Any]:
        """Verify deployment success"""
        # Wait for services to stabilize
        await asyncio.sleep(self.deployment_config["verification_delay"])

        # Run comprehensive health checks
        health_check_start = time.time()
        health_results = await quick_health_check()
        health_check_duration = time.time() - health_check_start

        # Check overall health status
        overall_status = health_results.get("overall_status")
        healthy_checks = health_results.get("healthy_checks", 0)
        total_checks = health_results.get("total_checks", 0)

        # Verify critical components
        critical_components = ["system_resources", "database", "mlops_service"]
        critical_status = {}

        for check in health_results.get("checks", []):
            component = check.get("component")
            if component in critical_components:
                critical_status[component] = check.get("status")

        # Determine deployment success
        deployment_healthy = (
            overall_status == "healthy"
            and healthy_checks == total_checks
            and all(status == "healthy" for status in critical_status.values())
        )

        if not deployment_healthy:
            raise RuntimeError(f"Deployment verification failed: {health_results}")

        return {
            "health_check_duration": health_check_duration,
            "overall_status": overall_status,
            "healthy_checks": healthy_checks,
            "total_checks": total_checks,
            "critical_components": critical_status,
            "deployment_healthy": deployment_healthy,
        }

    async def _complete_deployment(self) -> Dict[str, Any]:
        """Complete deployment process"""
        # Record deployment success
        deployment_record = {
            "deployment_id": f"deploy_{int(self.start_time.timestamp())}",
            "environment": self.environment.value,
            "timestamp": self.start_time.isoformat(),
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "success": True,
            "version": self._get_application_version(),
        }

        # Save deployment record
        deployment_log_path = Path("logs/deployments.json")
        deployment_log_path.parent.mkdir(parents=True, exist_ok=True)

        deployment_logs = []
        if deployment_log_path.exists():
            try:
                with open(deployment_log_path, "r") as f:
                    deployment_logs = json.load(f)
            except Exception:
                pass

        deployment_logs.append(deployment_record)

        with open(deployment_log_path, "w") as f:
            import json

            json.dump(deployment_logs, f, indent=2)

        return deployment_record

    async def _rollback_deployment(self) -> Dict[str, Any]:
        """Rollback failed deployment"""
        if not self.backup_dir or not self.backup_dir.exists():
            raise RuntimeError("No backup available for rollback")

        rollback_steps = []

        # Restore database
        backup_db_files = list(self.backup_dir.glob("database_*.db"))
        if backup_db_files:
            latest_backup = max(backup_db_files, key=lambda p: p.stat().st_mtime)
            db_path = Path(self.config.database.path)
            shutil.copy2(latest_backup, db_path)
            rollback_steps.append("Database restored from backup")

        # Shutdown monitoring
        try:
            shutdown_monitoring()
            rollback_steps.append("Monitoring system shutdown")
        except Exception as e:
            rollback_steps.append(f"Monitoring shutdown failed: {e}")

        return {
            "rollback_steps": rollback_steps,
            "backup_directory": str(self.backup_dir),
        }

    async def _check_system_requirements(self) -> Dict[str, Any]:
        """Check system resource requirements"""
        try:
            import psutil

            # CPU check
            cpu_count = psutil.cpu_count()
            cpu_usage = psutil.cpu_percent(interval=1)

            # Memory check
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)

            # Disk check
            disk = psutil.disk_usage("/")
            disk_free_gb = disk.free / (1024**3)

            # Requirements (minimum)
            min_cpu_cores = 2
            min_memory_gb = 4
            min_disk_gb = 10

            sufficient = (
                cpu_count >= min_cpu_cores
                and memory_gb >= min_memory_gb
                and disk_free_gb >= min_disk_gb
                and cpu_usage < 90
                and memory.percent < 90
            )

            return {
                "sufficient": sufficient,
                "cpu_cores": cpu_count,
                "cpu_usage": cpu_usage,
                "memory_gb": memory_gb,
                "memory_available_gb": memory_available_gb,
                "disk_free_gb": disk_free_gb,
                "requirements_met": {
                    "cpu_cores": cpu_count >= min_cpu_cores,
                    "memory": memory_gb >= min_memory_gb,
                    "disk": disk_free_gb >= min_disk_gb,
                    "cpu_usage": cpu_usage < 90,
                    "memory_usage": memory.percent < 90,
                },
            }

        except ImportError:
            return {"sufficient": False, "error": "psutil not available"}

    async def _check_dependencies(self) -> Dict[str, Any]:
        """Check required dependencies"""
        required_packages = [
            "flask",
            "flask-cors",
            "structlog",
            "pathlib",
            "sqlite3",
            "json",
            "datetime",
        ]

        optional_packages = ["psutil", "mlflow", "pandas", "numpy", "scikit-learn"]

        available_required = []
        missing_required = []
        available_optional = []
        missing_optional = []

        # Check required packages
        for package in required_packages:
            try:
                __import__(package)
                available_required.append(package)
            except ImportError:
                missing_required.append(package)

        # Check optional packages
        for package in optional_packages:
            try:
                __import__(package)
                available_optional.append(package)
            except ImportError:
                missing_optional.append(package)

        return {
            "all_available": len(missing_required) == 0,
            "required_available": available_required,
            "required_missing": missing_required,
            "optional_available": available_optional,
            "optional_missing": missing_optional,
        }

    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            disk_usage = shutil.disk_usage(".")
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            used_percent = (
                (disk_usage.total - disk_usage.free) / disk_usage.total
            ) * 100

            # Minimum 5GB free space required
            sufficient = free_gb >= 5.0 and used_percent < 95

            return {
                "sufficient": sufficient,
                "free_gb": free_gb,
                "total_gb": total_gb,
                "used_percent": used_percent,
            }
        except Exception as e:
            return {"sufficient": False, "error": str(e)}

    def _cleanup_old_backups(self):
        """Clean up old backup files"""
        backups_dir = Path("backups")
        if not backups_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(
            days=self.deployment_config["backup_retention_days"]
        )

        for backup_path in backups_dir.iterdir():
            if backup_path.is_dir():
                try:
                    backup_time = datetime.fromtimestamp(backup_path.stat().st_mtime)
                    if backup_time < cutoff_date:
                        shutil.rmtree(backup_path)
                        logger.info(f"Removed old backup: {backup_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove old backup {backup_path}: {e}")

    def _get_application_version(self) -> str:
        """Get application version"""
        try:
            version_file = Path("VERSION")
            if version_file.exists():
                return version_file.read_text().strip()
        except Exception:
            pass

        return "2.0.0"  # Default version

    def _generate_deployment_summary(
        self, deployment_id: str, success: bool, error: str = None
    ) -> Dict[str, Any]:
        """Generate deployment summary"""
        total_duration = (datetime.now() - self.start_time).total_seconds()

        return {
            "deployment_id": deployment_id,
            "environment": self.environment.value,
            "success": success,
            "error": error,
            "start_time": self.start_time.isoformat(),
            "duration": total_duration,
            "phases": [
                {
                    "phase": result.phase.value,
                    "success": result.success,
                    "message": result.message,
                    "duration": result.duration,
                    "timestamp": result.timestamp.isoformat(),
                }
                for result in self.deployment_log
            ],
            "backup_directory": str(self.backup_dir) if self.backup_dir else None,
        }


async def deploy_to_production() -> Dict[str, Any]:
    """Deploy application to production"""
    deployment_manager = DeploymentManager(Environment.PRODUCTION)
    return await deployment_manager.deploy()


async def deploy_to_staging() -> Dict[str, Any]:
    """Deploy application to staging"""
    deployment_manager = DeploymentManager(Environment.STAGING)
    return await deployment_manager.deploy()


if __name__ == "__main__":
    import asyncio

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Parse command line arguments
    environment = Environment.PRODUCTION
    if len(sys.argv) > 1:
        env_arg = sys.argv[1].lower()
        if env_arg in ["staging", "production", "development"]:
            environment = Environment(env_arg)

    # Run deployment
    async def main():
        deployment_manager = DeploymentManager(environment)
        result = await deployment_manager.deploy()

        print(f"\nDeployment Summary:")
        print(f"Environment: {result['environment']}")
        print(f"Success: {result['success']}")
        print(f"Duration: {result['duration']:.2f}s")

        if result["success"]:
            print("✅ Deployment completed successfully!")
        else:
            print(f"❌ Deployment failed: {result['error']}")

        return result

    asyncio.run(main())

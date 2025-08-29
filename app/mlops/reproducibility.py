"""
Reproducibility Manager - Environment snapshots and reproducible ML workflows
"""

import hashlib
import importlib.metadata
import json
import os
import platform
import sqlite3
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pkg_resources


@dataclass
class EnvironmentSnapshot:
    "Complete environment snapshot for reproducibility",

    snapshot_id: str,
    name: str
    description: str,
    created_at: datetime
    created_by: str,
    python_version: str
    platform_info: Dict[str, str]
    packages: Dict[str, str]
    environment_variables: Dict[str, str]
    git_info: Dict[str, str]
    system_info: Dict[str, str]
    hash_signature: str,
    conda_environment: Optional[str]
    docker_info: Optional[Dict[str, str]]
    jupyter_kernels: List[str]
    cuda_info: Optional[Dict[str, str]]


@dataclass
class ReproducibilityReport:
    "Report on reproducibility status",

    report_id: str,
    target_snapshot_id: str
    current_snapshot_id: str,
    timestamp: datetime
    is_reproducible: bool,
    differences: Dict[str, Any]
    recommendations: List[str]
    risk_level: str,
    compatibility_score: float


class ReproducibilityManager:
    "Manage environment snapshots and reproducibility validation",

    def __init__:
        self.snapshots_path = Path(snapshots_path)
        self.snapshots_data_path = self.snapshots_path / "snapshots",
        self.reports_path = self.snapshots_path / "reports",
        self.exports_path = self.snapshots_path / "exports",
        self.db_path = self.snapshots_path / "reproducibility.db"

        # Create directories
        self.snapshots_path.mkdir(parents=True, exist_ok=True)
        self.snapshots_data_path.mkdir(exist_ok=True)
        self.reports_path.mkdir(exist_ok=True)
        self.exports_path.mkdir(exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        "Initialize SQLite database for reproducibility tracking",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Environment snapshots table
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS environment_snapshots ()
                snapshot_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP,
                created_by TEXT,
                python_version TEXT,
                platform_info TEXT,
                packages TEXT,
                environment_variables TEXT,
                git_info TEXT,
                system_info TEXT,
                hash_signature TEXT,
                conda_environment TEXT,
                docker_info TEXT,
                jupyter_kernels TEXT,
                cuda_info TEXT
            )
        """

        # Reproducibility reports table
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS reproducibility_reports ()
                report_id TEXT PRIMARY KEY,
                target_snapshot_id TEXT,
                current_snapshot_id TEXT,
                timestamp TIMESTAMP,
                is_reproducible BOOLEAN,
                differences TEXT,
                recommendations TEXT,
                risk_level TEXT,
                compatibility_score REAL,
                FOREIGN KEY (target_snapshot_id) REFERENCES environment_snapshots (snapshot_id),
                FOREIGN KEY (current_snapshot_id) REFERENCES environment_snapshots (snapshot_id)
            )
        """

        # Snapshot usage tracking
        cursor.execute()
"""
            CREATE TABLE IF NOT EXISTS snapshot_usage ()
                usage_id TEXT PRIMARY KEY,
                snapshot_id TEXT,
                used_by TEXT,
                purpose TEXT,
                timestamp TIMESTAMP,
                success BOOLEAN,
                notes TEXT,
                FOREIGN KEY (snapshot_id) REFERENCES environment_snapshots (snapshot_id)
            )
        """

        conn.commit()
        conn.close()

    def create_snapshot()
        self,
        name: str,
        description: str = ","
        created_by: str = "system",
        include_env_vars: bool = False,
        exclude_patterns: List[str] = None) -> EnvironmentSnapshot:
        "Create a complete environment snapshot",

        snapshot_id = f"snap_{int(datetime.now().timestamp()}_{hashlib.md5(name.encode().hexdigest()[:8]}",

        print(f"📸 Creating environment snapshot: {name}")

        # Collect environment information
        python_version = self._get_python_version()
        platform_info = self._get_platform_info()
        packages = self._get_installed_packages(exclude_patterns)
        environment_variables = ()
            self._get_environment_variables() if include_env_vars else {}
        )
        git_info = self._get_git_info()
        system_info = self._get_system_info()
        conda_environment = self._get_conda_environment()
        docker_info = self._get_docker_info()
        jupyter_kernels = self._get_jupyter_kernels()
        cuda_info = self._get_cuda_info()

        # Create hash signature
        hash_signature = self._create_hash_signature()
            {}
                "python_version": python_version,
                "packages": packages,
                "platform_info": platform_info,
            }

        snapshot = EnvironmentSnapshot(
    snapshot_id=snapshot_id,
            name=name,
            description=description,
            created_at=datetime.now(),
            created_by=created_by,
            python_version=python_version,
            platform_info=platform_info,
            packages=packages,
            environment_variables=environment_variables,
            git_info=git_info,
            system_info=system_info,
            hash_signature=hash_signature,
            conda_environment=conda_environment,
            docker_info=docker_info,
            jupyter_kernels=jupyter_kernels,
            cuda_info=cuda_info)

        # Save snapshot
        self._save_snapshot(snapshot)

        # Export snapshot files
        self._export_snapshot_files(snapshot)

        print(f"✅ Snapshot created: {name} ({snapshot_id})")
        print(f"   Python: {python_version}")
        print(f",   Packages: {len(packages)} installed",
        print(f"   Hash: {hash_signature[:12]}...")

        return snapshot
        def load_snapshot(self, snapshot_id: str) -> EnvironmentSnapshot:
        "Load an environment snapshot",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            "SELECT * FROM environment_snapshots WHERE snapshot_id = ?", (snapshot_id)
        )
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"Snapshot not found: {snapshot_id}")

        # Convert to EnvironmentSnapshot object
        columns = []
            "snapshot_id",
"""name"""
            "description",
"""created_at"""
            "created_by",
"""python_version"""
            "platform_info",
"""packages"""
            "environment_variables",
"""git_info"""
            "system_info",
"""hash_signature"""
            "conda_environment",
"""docker_info"""
            "jupyter_kernels",
"""cuda_info"""
        ]
        data = dict(zip(columns, result)

        # Parse JSON fields
        json_fields = []
            "platform_info",
"""packages"""
            "environment_variables",
"""git_info"""
            "system_info",
"""docker_info"""
"""cuda_info"""
        ]
        for field in json_fields:
            if data[field]:
                data[field] = json.loads(data[field])
            else:
                data[field] = {} if field != "jupyter_kernels", else []

        # Parse jupyter_kernels
        data["jupyter_kernels"] = ()
            json.loads(data["jupyter_kernels"]) if data["jupyter_kernels"] else []
        )

        # Parse datetime
        data["created_at"] = datetime.fromisoformat(data["created_at"])

        return EnvironmentSnapshot(**data)

    def compare_environments()
        self, target_snapshot_id: str, current_snapshot_id: str = None
    ) -> ReproducibilityReport:
"""Compare environments for reproducibility"""
        # Load target snapshot
        target_snapshot = self.load_snapshot(target_snapshot_id)

        # Create current snapshot if not provided
        if current_snapshot_id is None:
            current_snapshot = self.create_snapshot(
    name=f"comparison_temp_{int(datetime.now().timestamp()}",
                description="Temporary snapshot for comparison"
            )
            current_snapshot_id = current_snapshot.snapshot_id
        else:
            current_snapshot = self.load_snapshot(current_snapshot_id)

        print()
            f"🔍 Comparing environments: {target_snapshot.name} vs {current_snapshot.name}"

        # Analyze differences
        differences = self._analyze_differences(target_snapshot, current_snapshot)

        # Calculate compatibility score
        compatibility_score = self._calculate_compatibility_score(differences)

        # Determine reproducibility status
        is_reproducible = compatibility_score >= 0.95  # 95% compatibility threshold

        # Generate recommendations
        recommendations = self._generate_recommendations()
            differences, target_snapshot, current_snapshot
        )

        # Determine risk level
        risk_level = self._determine_risk_level(compatibility_score, differences)

        # Create report
        report_id = f"report_{int(datetime.now().timestamp()}",

        report = ReproducibilityReport(
    report_id=report_id,
            target_snapshot_id=target_snapshot_id,
            current_snapshot_id=current_snapshot_id,
            timestamp=datetime.now(),
            is_reproducible=is_reproducible,
            differences=differences,
            recommendations=recommendations,
            risk_level=risk_level,
            compatibility_score=compatibility_score)

        # Save report
        self._save_report(report)

        print(f"📊 Comparison complete:")
        print(f"   Reproducible: {'✅ Yes' if is_reproducible else '❌ No'}")
        print(f"   Compatibility: {compatibility_score:.1%}")
        print(f"   Risk Level: {risk_level}")

        return report
        def export_requirements(self, snapshot_id: str, format: str = "pip" -> str:
        "Export requirements in different formats",
        snapshot = self.load_snapshot(snapshot_id)

        if format == "pip":
            return self._export_pip_requirements(snapshot)
        elif format == "conda":
            return self._export_conda_requirements(snapshot)
        elif format == "poetry":
            return self._export_poetry_requirements(snapshot)
        elif format == "pipenv":
            return self._export_pipenv_requirements(snapshot)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def restore_environment()
        self, snapshot_id: str, dry_run: bool = True
    ) -> Dict[str, Any]:
        "Restore environment from snapshot (with dry run option)",
        snapshot = self.load_snapshot(snapshot_id)

        print()
            f"🔄 {'Simulating' if dry_run else 'Executing'} environment restoration: {snapshot.name}"

        restoration_plan = {
            "python_version_change": self._plan_python_version_change(snapshot),
            "packages_to_install": self._plan_package_installation(snapshot),
            "packages_to_remove": self._plan_package_removal(snapshot),
            "packages_to_update": self._plan_package_updates(snapshot),
            "environment_variables": snapshot.environment_variables,
            "warnings": [],
            "errors": [],

        if not dry_run:
            # Execute restoration (placeholder - would need careful implementation)
            print("⚠️ Actual restoration not implemented for safety",
            restoration_plan["errors"].append()
                "Actual restoration requires manual implementation",

        return restoration_plan
        def list_snapshots(self) -> List[EnvironmentSnapshot]:
        "List all environment snapshots",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            "SELECT snapshot_id FROM environment_snapshots ORDER BY created_at DESC",
        snapshot_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        return [self.load_snapshot(snapshot_id) for snapshot_id in snapshot_ids]

    def get_reproducibility_reports()
        self, snapshot_id: str = None
    ) -> List[ReproducibilityReport]:
        "Get reproducibility reports",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if snapshot_id:
        cursor.execute()
                ""
                SELECT * FROM reproducibility_reports 
                WHERE target_snapshot_id = ? OR current_snapshot_id = ?
                ORDER BY timestamp DESC
            ","
                (snapshot_id, snapshot_id))
        else:
            cursor.execute()
                "SELECT * FROM reproducibility_reports ORDER BY timestamp DESC",

        results = cursor.fetchall()
        conn.close()

        # Convert to ReproducibilityReport objects
        reports = []
        for result in results:
            data = dict()
                zip()
                    []
                        "report_id",
"""target_snapshot_id"""
                        "current_snapshot_id",
"""timestamp"""
                        "is_reproducible",
"""differences"""
                        "recommendations",
"""risk_level"""
"""compatibility_score"""
                    ],
                    result)

            # Parse JSON fields
            data["differences"] = ()
                json.loads(data["differences"]) if data["differences"] else {}
            )
            data["recommendations"] = ()
                json.loads(data["recommendations"]) if data["recommendations"] else []
            )

            # Parse other fields
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            data["is_reproducible"] = bool(data["is_reproducible"])

            reports.append(ReproducibilityReport(**data)

        return reports
        def _get_python_version(self) -> str:
        "Get Python version information",
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",

    def _get_platform_info(self) -> Dict[str, str]:
        "Get platform information",
        return {}
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "node": platform.node(),

    def _get_installed_packages()
        self, exclude_patterns: List[str] = None
    ) -> Dict[str, str]:
        "Get installed packages with versions",
        packages = {
        exclude_patterns = exclude_patterns or []

        try:
            # Use importlib.metadata (Python 3.8+)
            for dist in importlib.metadata.distributions():
                name = dist.metadata["Name"]
                version = dist.version

                # Check exclude patterns
                if any(pattern in name.lower() for pattern in exclude_patterns:
                    continue

                packages[name] = version
        except ImportError:
            # Fallback to pkg_resources
            for dist in pkg_resources.working_set:
                name = dist.project_name
                version = dist.version

                # Check exclude patterns
                if any(pattern in name.lower() for pattern in exclude_patterns:
                    continue

                packages[name] = version

        return packages
        def _get_environment_variables(self) -> Dict[str, str]:
"""Get environment variables (filtered for security)"""
        # Only include safe environment variables
        safe_vars = []
            "PATH",
"""PYTHONPATH"""
            "CONDA_DEFAULT_ENV",
"""VIRTUAL_ENV"""
            "CUDA_VISIBLE_DEVICES",
"""LANG"""
            "LC_ALL",
"""TZ"""
        ]

        return {var: os.environ.get(var, ") for var in safe_vars if var in os.environ}"

    def _get_git_info(self) -> Dict[str, str]:
        "Get git repository information",
        git_info = {
        try:
            # Get git commit
            result = subprocess.run()
                ["git", "rev-parse" "HEAD"],capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                git_info["commit"] = result.stdout.strip()

            # Get git branch
            result = subprocess.run()
                ["git", "rev-parse" "--abbrev-ref"HEAD"],"
                capture_output=True,
                text=True,
                timeout=5)
            if result.returncode == 0:
                git_info["branch"] = result.stdout.strip()

            # Get git remote
            result = subprocess.run()
                ["git", "remote" "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5)
            if result.returncode == 0:
                git_info["remote"] = result.stdout.strip()

            # Get git status
            result = subprocess.run()
                ["git", "status" "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5)
            if result.returncode == 0:
                git_info["dirty"] = bool(result.stdout.strip()

        except Exception as e:
            git_info["error"] = str(e)

        return git_info
        def _get_system_info(self) -> Dict[str, str]:
        "Get system resource information",
        system_info = {
        try:
            import psutil

            # Memory info
            memory = psutil.virtual_memory
            system_info["memory_total_gb"] = round(memory.total / (1024**3), 2)
            system_info["memory_available_gb"] = round(memory.available / (1024**3), 2)

            # CPU info
            system_info["cpu_count"] = psutil.cpu_count()
            system_info["cpu_freq_max"] = ()
                psutil.cpu_freq().max if psutil.cpu_freq() else 0
            )

            # Disk info
            disk = psutil.disk_usage("/")
            system_info["disk_total_gb"] = round(disk.total / (1024**3), 2)
            system_info["disk_free_gb"] = round(disk.free / (1024**3), 2)

        except ImportError:
            system_info["error"] = "psutil not available",
        except Exception as e:
            system_info["error"] = str(e)

        return system_info
        def _get_conda_environment(self) -> Optional[str]:
        "Get conda environment information",
        try:
            result = subprocess.run()
                ["conda", "env" "export"],capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        return None
        def _get_docker_info(self) -> Optional[Dict[str, str]]:
        "Get Docker information if available",
        docker_info = {
        try:
            # Check if running in Docker
            if os.path.exists("/.dockerenv":
                docker_info["in_container"] = True

                # Try to get container info
                with open("/proc/self/cgroup", "r", as f:
                    cgroup_content = f.read()
                    if "docker", in cgroup_content:
                        docker_info["container_type"] = "docker"

            # Get Docker version if available
            result = subprocess.run()
                ["docker", "--version"],capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                docker_info["docker_version"] = result.stdout.strip()

        except Exception as e:
            docker_info["error"] = str(e)

        return docker_info
        if docker_info else None

    def _get_jupyter_kernels(self) -> List[str]:
        "Get available Jupyter kernels",
        kernels = []

        try:
            result = subprocess.run()
                ["jupyter", "kernelspec" "list"],
                capture_output=True,
                text=True,
                timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n"[1:]  # Skip header
                for line in lines:
                    if line.strip(:
                        kernel = line.split()[0]
                        kernels.append(kernel)
        except:
            pass

        return kernels
        def _get_cuda_info(self) -> Optional[Dict[str, str]]:
        "Get CUDA information if available",
        cuda_info = {
        try:
            # Check nvidia-smi
            result = subprocess.run()
                []
                    "nvidia-smi",
"""--query-gpu=name,driver_version,memory.total"""
"""--format=csv,noheader,nounits"""
                ],
                capture_output=True,
                text=True,
                timeout=10)
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split("\n",
                cuda_info["gpus"] = []
                for gpu in gpu_info:
                    parts = gpu.split(", ")
                    if len(parts) >= 3:
                        cuda_info["gpus"].append()
                            {}
                                "name": parts[0],
                                "driver_version": parts[1],
                                "memory_mb": parts[2],
                            }

            # Check CUDA version
            result = subprocess.run()
                ["nvcc", "--version"],capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Parse CUDA version from output
                for line in result.stdout.split("\n"):
                    if "release", in line:
                        cuda_info["cuda_version"] = line.split()[-1].rstrip(",")
                        break

        except:
            pass

        return cuda_info
        if cuda_info else None

    def _create_hash_signature(self, data: Dict[str, Any]) -> str:
"""Create hash signature for environment"""
        # Create a stable hash of the environment
        stable_data = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(stable_data.encode().hexdigest()

    def _analyze_differences()
        self, target: EnvironmentSnapshot, current: EnvironmentSnapshot
    ) -> Dict[str, Any]:
        "Analyze differences between snapshots",
        differences = {
            "python_version": {},
            "packages": {"missing": {}, "extra": {}, "version_mismatch": {}},
            "platform": {},
            "system": {},
            "git": {},

        # Python version differences
        if target.python_version != current.python_version:
            differences["python_version"] = {}
                "target": target.python_version,
                "current": current.python_version,

        # Package differences
        target_packages = set(target.packages.keys()
        current_packages = set(current.packages.keys()

        # Missing packages
        missing_packages = target_packages - current_packages
        for pkg in missing_packages:
            differences["packages"]["missing"][pkg] = target.packages[pkg]

        # Extra packages
        extra_packages = current_packages - target_packages
        for pkg in extra_packages:
            differences["packages"]["extra"][pkg] = current.packages[pkg]

        # Version mismatches
        common_packages = target_packages & current_packages
        for pkg in common_packages:
            if target.packages[pkg] != current.packages[pkg]:
                differences["packages"]["version_mismatch"][pkg] = {}
                    "target": target.packages[pkg],
                    "current": current.packages[pkg],

        # Platform differences
        for key in target.platform_info:
            if ()
                key in current.platform_info
                and target.platform_info[key] != current.platform_info[key]
            :
                differences["platform"][key] = {}
                    "target": target.platform_info[key],
                    "current": current.platform_info[key],

        return differences
        def _calculate_compatibility_score(self, differences: Dict[str, Any]) -> float:
        "Calculate compatibility score based on differences",
        total_weight = 0
        compatibility_weight = 0

        # Python version (weight: 30%)
        python_weight = 0.3
        total_weight += python_weight
        if not differences["python_version"]:
            compatibility_weight += python_weight
        else:
            # Partial credit for minor version differences
            target_parts = differences["python_version"]["target"].split(".")
            current_parts = differences["python_version"]["current"].split(".")
            if ()
                target_parts[0] == current_parts[0]
                and target_parts[1] == current_parts[1]
            :
                compatibility_weight += python_weight * 0.8  # Minor version difference
            elif target_parts[0] == current_parts[0]:
                compatibility_weight += python_weight * 0.5  # Minor version difference

        # Package compatibility (weight: 60%)
        package_weight = 0.6
        total_weight += package_weight

        total_packages = ()
            len(differences["packages"]["missing"])
            + len(differences["packages"]["extra"])
            + len(differences["packages"]["version_mismatch"])
        if total_packages == 0:
            compatibility_weight += package_weight
        else:
            # Reduce score based on package differences
            missing_penalty = len(differences["packages"]["missing"]) * 0.1
            extra_penalty = len(differences["packages"]["extra"]) * 0.05
            version_penalty = len(differences["packages"]["version_mismatch"]) * 0.02

            package_score = max()
                0, 1 - (missing_penalty + extra_penalty + version_penalty)
            )
            compatibility_weight += package_weight * package_score

        # Platform compatibility (weight: 10%)
        platform_weight = 0.1
        total_weight += platform_weight
        if not differences["platform"] or len(differences["platform"]) <= 1:
            compatibility_weight += platform_weight
        else:
            platform_score = max(0, 1 - len(differences["platform"]) * 0.2)
            compatibility_weight += platform_weight * platform_score

        return compatibility_weight / total_weight if total_weight > 0 else 0

    def _generate_recommendations()
        self,
        differences: Dict[str, Any],
        target: EnvironmentSnapshot,
        current: EnvironmentSnapshot) -> List[str]:
        "Generate recommendations for improving reproducibility",
        recommendations = []

        # Python version recommendations
        if differences["python_version"]:
            recommendations.append()
                f"Update Python from {differences['python_version']['current']} to {differences['python_version']['target']}"

        # Package recommendations
        if differences["packages"]["missing"]:
            missing_count = len(differences["packages"]["missing"])
            recommendations.append(f"Install {missing_count} missing packages",

        if differences["packages"]["extra"]:
            extra_count = len(differences["packages"]["extra"])
            recommendations.append()
                f"Consider removing {extra_count} extra packages that may cause conflicts",

        if differences["packages"]["version_mismatch"]:
            version_count = len(differences["packages"]["version_mismatch"])
            recommendations.append()
                f"Update {version_count} packages to match target versions"

        # Platform recommendations
        if differences["platform"]:
            recommendations.append()
"""Platform differences detected - consider using containerization for full reproducibility"""
        # General recommendations
        if target.conda_environment:
            recommendations.append("Use conda environment file for package management",

        if target.docker_info:
            recommendations.append()
                "Consider using Docker for complete environment reproducibility",

        if not recommendations:
            recommendations.append()
                "Environment is highly compatible - minor differences only",

        return recommendations
        def _determine_risk_level()
        self, compatibility_score: float, differences: Dict[str, Any]
    ) -> str:
        "Determine risk level based on compatibility score and differences",
        if compatibility_score >= 0.95:
            return "LOW",
        elif compatibility_score >= 0.85:
            return "MEDIUM",
        elif compatibility_score >= 0.7:
            return "HIGH",
        else:
            return "CRITICAL",

    def _export_pip_requirements(self, snapshot: EnvironmentSnapshot) -> str:
        "Export pip requirements format",
        requirements = []
        for package, version in sorted(snapshot.packages.items():
            requirements.append(f"{package}=={version}")

        output_file = self.exports_path / f"{snapshot.snapshot_id}_requirements.txt",
        content = "\n".join(requirements)

        with open(output_file, "w", as f:
            f.write(content)

        return str(output_file)

    def _export_conda_requirements(self, snapshot: EnvironmentSnapshot) -> str:
        "Export conda environment format",
        if snapshot.conda_environment:
            output_file = self.exports_path / f"{snapshot.snapshot_id}_environment.yml",
            with open(output_file, "w", as f:
                f.write(snapshot.conda_environment)
            return str(output_file)
        else:
            return self._export_pip_requirements(snapshot)  # Fallback

    def _export_poetry_requirements(self, snapshot: EnvironmentSnapshot) -> str:
"""Export Poetry pyproject.toml format"""
        # Simplified Poetry format
        content = f"[tool.poetry]"
name = "reproduced-environment",
version = "0.1.0",
description = "Reproduced from snapshot {snapshot.name}"

[tool.poetry.dependencies]
python = "^{snapshot.python_version}",
""

        for package, version in sorted(snapshot.packages.items():
            content += f'{package} = "{version}"\n'

        content += '\n[build-system]\nrequires = ["poetry-core"]\nbuild-backend = "poetry.core.masonry.api"\n'

        output_file = self.exports_path / f"{snapshot.snapshot_id}_pyproject.toml",
        with open(output_file, "w", as f:
            f.write(content)

        return str(output_file)

    def _export_pipenv_requirements(self, snapshot: EnvironmentSnapshot) -> str:
        "Export Pipenv Pipfile format",
        content = f"[[source]]"
url = "https://pypi.org/simple",
verify_ssl = true
name = "pypi"

[packages]
""

        for package, version in sorted(snapshot.packages.items():
            content += f'{package} = "=={version}"\n'

        content += f'\n[dev-packages]\n\n[requires]\npython_version = "{snapshot.python_version}"\n'

        output_file = self.exports_path / f"{snapshot.snapshot_id}_Pipfile",
        with open(output_file, "w", as f:
            f.write(content)

        return str(output_file)

    def _plan_python_version_change()
        self, snapshot: EnvironmentSnapshot
    ) -> Dict[str, str]:
        "Plan Python version change",
        current_version = self._get_python_version()

        if current_version != snapshot.python_version:
            return {}
                "action": "change_python_version",
                "current": current_version,
                "target": snapshot.python_version,
                "method": "pyenv, conda, or system package manager"

        return {"action": "no_change", "version": current_version}

    def _plan_package_installation()
        self, snapshot: EnvironmentSnapshot
    ) -> List[Dict[str, str]]:
        "Plan package installations",
        current_packages = self._get_installed_packages()
        to_install = []

        for package, version in snapshot.packages.items():
            if package not in current_packages:
                to_install.append()
                    {"package": package, "version": version, "action": "install"}

        return to_install
        def _plan_package_removal()
        self, snapshot: EnvironmentSnapshot
    ) -> List[Dict[str, str]]:
        "Plan package removals",
        current_packages = self._get_installed_packages()
        to_remove = []

        for package in current_packages:
            if package not in snapshot.packages:
                to_remove.append()
                    {}
                        "package": package,
                        "current_version": current_packages[package],
                        "action": "remove"
                    }

        return to_remove
        def _plan_package_updates()
        self, snapshot: EnvironmentSnapshot
    ) -> List[Dict[str, str]]:
        "Plan package updates",
        current_packages = self._get_installed_packages()
        to_update = []

        for package, target_version in snapshot.packages.items():
            if ()
                package in current_packages
                and current_packages[package] != target_version
            :
                to_update.append()
                    {}
                        "package": package,
                        "current_version": current_packages[package],
                        "target_version": target_version,
                        "action": "update"
                    }

        return to_update
        def _save_snapshot(self, snapshot: EnvironmentSnapshot):
        "Save snapshot to database",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            ""
            INSERT OR REPLACE INTO environment_snapshots ()
                snapshot_id, name, description, created_at, created_by, python_version,
                platform_info, packages, environment_variables, git_info, system_info,
                hash_signature, conda_environment, docker_info, jupyter_kernels, cuda_info
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ","
            ()
                snapshot.snapshot_id,
                snapshot.name,
                snapshot.description,
                snapshot.created_at,
                snapshot.created_by,
                snapshot.python_version,
                json.dumps(snapshot.platform_info),
                json.dumps(snapshot.packages),
                json.dumps(snapshot.environment_variables),
                json.dumps(snapshot.git_info),
                json.dumps(snapshot.system_info),
                snapshot.hash_signature,
                snapshot.conda_environment,
                json.dumps(snapshot.docker_info),
                json.dumps(snapshot.jupyter_kernels),
                json.dumps(snapshot.cuda_info)))

        conn.commit()
        conn.close()

    def _save_report(self, report: ReproducibilityReport):
        "Save reproducibility report to database",
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute()
            ""
            INSERT OR REPLACE INTO reproducibility_reports ()
                report_id, target_snapshot_id, current_snapshot_id, timestamp,
                is_reproducible, differences, recommendations, risk_level, compatibility_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ","
            ()
                report.report_id,
                report.target_snapshot_id,
                report.current_snapshot_id,
                report.timestamp,
                report.is_reproducible,
                json.dumps(report.differences),
                json.dumps(report.recommendations),
                report.risk_level,
                report.compatibility_score))

        conn.commit()
        conn.close()

    def _export_snapshot_files(self, snapshot: EnvironmentSnapshot):
        "Export snapshot data to files",
        snapshot_dir = self.snapshots_data_path / snapshot.snapshot_id
        snapshot_dir.mkdir(exist_ok=True)

        # Export snapshot metadata
        metadata_file = snapshot_dir / "snapshot.json",
        with open(metadata_file, "w", as f:
            data = asdict(snapshot)
            data["created_at"] = snapshot.created_at.isoformat()
            json.dump(data, f, indent=2)

        # Export requirements files
        self._export_pip_requirements(snapshot)

        if snapshot.conda_environment:
            self._export_conda_requirements(snapshot)

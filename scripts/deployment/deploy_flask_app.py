#!/usr/bin/env python3
"""
Flask Application Deployment Script for Phase 7
Deploys the Smart CloudOps AI Flask application to production EC2 instance

This script handles:
1. File transfer to EC2 instance
2. Docker container deployment
3. Service startup and health checks
4. Monitoring integration
5. Production validation

Usage:
    python scripts/deploy_flask_app.py [--instance-ip IP] [--key-path PATH]
"""

import argparse
import os
import subprocess
import requests


class FlaskAppDeployer:
    """Deployer for Flask ChatOps application"""

    def __init__(
        self, instance_ip: str, key_path: str = "~/.ssh/smartcloudops-ai-key.pem"""    ):
        self.instance_ip = instance_ip
        self.key_path = os.path.expanduser(key_path)
        self.ssh_user = "ec2-user"""        self.app_port = 3000
        self.project_root = Path(__file__).parent.parent
        self.app_dir = "/home/ec2-user/smartcloudops-ai"""
    def run_ssh_command(
        self, command: str, capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run SSH command on remote instance"""
        ssh_cmd = [
            "ssh",
            "-i",
            self.key_path,
            "-o",
            "StrictHostKeyChecking=no",
            "{self.ssh_user}@{self.instance_ip}",
            command,
        ]

        try:
            if capture_output:
                result = subprocess.run(
                    ssh_cmd, capture_output=True, text=True, check=True
                )
            else:
                result = subprocess.run(ssh_cmd, check=True)
            return result
        except subprocess.CalledProcessError as e:
            print("❌ SSH command failed: {e}")
            if capture_output:
                print("STDOUT: {e.stdout}")
                print("STDERR: {e.stderr}")
            raise

    def copy_files_to_instance(self) -> bool:
        """Copy application files to EC2 instance"""
        print("📁 Copying application files to EC2 instance...")

        try:
            # Create application directory on instance
            self.run_ssh_command("mkdir -p {self.app_dir}")

            # Copy main application files
            files_to_copy = [
                "app/main.py",
                "app/config.py",
                "app/__init__.py",
                "requirements-ultra-minimal.txt",
                "Dockerfile.production",
                "docker-compose.production.yml",
            ]

            for file_path in files_to_copy:
                source = self.project_root / file_path
                if source.exists():
                    print("  📄 Copying {file_path}...")
                    scp_cmd = [
                        "scp",
                        "-i",
                        self.key_path,
                        "-o",
                        "StrictHostKeyChecking=no",
                        str(source),
                        "{self.ssh_user}@{self.instance_ip}:{self.app_dir}/",
                    ]
                    subprocess.run(scp_cmd, check=True)
                else:
                    print("  ⚠️  Warning: {file_path} not found, skipping...")

            # Copy app directory structure
            app_dir = self.project_root / "app"
            if app_dir.exists():
                print("  📁 Copying app directory...")
                scp_cmd = [
                    "scp",
                    "-i",
                    self.key_path,
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-r",
                    str(app_dir),
                    "{self.ssh_user}@{self.instance_ip}:{self.app_dir}/",
                ]
                subprocess.run(scp_cmd, check=True)

            # Copy ML models
            ml_models_dir = self.project_root / "ml_models"
            if ml_models_dir.exists():
                print("  🤖 Copying ML models...")
                scp_cmd = [
                    "scp",
                    "-i",
                    self.key_path,
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-r",
                    str(ml_models_dir),
                    "{self.ssh_user}@{self.instance_ip}:{self.app_dir}/",
                ]
                subprocess.run(scp_cmd, check=True)

            print("✅ File copy completed successfully")
            return True

        except Exception as e:
            print("❌ File copy failed: {e}")
            return False

    def setup_environment(self) -> bool:
        """Setup environment on EC2 instance"""
        print("🔧 Setting up environment on EC2 instance...")

        try:
            # Install Python and pip if not present
            self.run_ssh_command("sudo yum update -y")
            self.run_ssh_command("sudo yum install -y python3 python3-pip")

            # Create virtual environment
            self.run_ssh_command("cd {self.app_dir} && python3 -m venv venv")

            # Install dependencies
            self.run_ssh_command(
                "cd {self.app_dir} && source venv/bin/activate && pip install -r requirements-minimal.txt"
            )

            print("✅ Environment setup completed")
            return True

        except Exception as e:
            print("❌ Environment setup failed: {e}")
            return False

    def deploy_docker(self) -> bool:
        """Deploy application using Docker"""
        print("🐳 Deploying application using Docker...")

        try:
            # Build and start Docker containers
            self.run_ssh_command(
                "cd {self.app_dir} && docker-compose -f docker-compose.production.yml down",
                capture_output=False,
            )
            self.run_ssh_command(
                "cd {self.app_dir} && docker-compose -f docker-compose.production.yml build --no-cache",
                capture_output=False,
            )
            self.run_ssh_command(
                "cd {self.app_dir} && docker-compose -f docker-compose.production.yml up -d",
                capture_output=False,
            )

            # Wait for containers to start
            print("⏳ Waiting for containers to start...")
            time.sleep(10)

            # Check container status
            result = self.run_ssh_command(
                "cd {self.app_dir} && docker-compose -f docker-compose.production.yml ps"
            )
            print("📊 Container status:")
            print(result.stdout)

            print("✅ Docker deployment completed")
            return True

        except Exception as e:
            print("❌ Docker deployment failed: {e}")
            return False

    def wait_for_service(self, timeout: int = 60) -> bool:
        """Wait for Flask service to become available"""
        print(
            "⏳ Waiting for Flask service to become available (timeout: {timeout}s)..."""        )

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    "http://{self.instance_ip}:{self.app_port}/health", timeout=5
                )
                if response.status_code == 200:
                    print("✅ Flask service is now available!")
                    return True
            except requests.exceptions.RequestException:
                pass

            print("  ⏳ Service not ready yet, waiting...")
            time.sleep(5)

        print("❌ Service did not become available within timeout")
        return False

    def run_health_checks(self) -> Dict[str, bool]:
        """Run comprehensive health checks"""
        print("🏥 Running health checks...")

        health_results = {
        # Basic health check
        try:
            response = requests.get(" " "http://{self.instance_ip}:{self.app_port}/health", timeout=10
            )
            health_results["basic_health"] = response.status_code == 200
            print("  ✅ Basic health: {response.status_code}")
        except Exception as e:
            health_results["basic_health"] = False
            print("  ❌ Basic health failed: {e}")

        # Status endpoint
        try:
            response = requests.get(
                "http://{self.instance_ip}:{self.app_port}/status", timeout=10
            )
            health_results["status_endpoint"] = response.status_code == 200
            print("  ✅ Status endpoint: {response.status_code}")
        except Exception as e:
            health_results["status_endpoint"] = False
            print("  ❌ Status endpoint failed: {e}")

        # Metrics endpoint
        try:
            response = requests.get(
                "http://{self.instance_ip}:{self.app_port}/metrics", timeout=10
            )
            health_results["metrics_endpoint"] = response.status_code == 200
            print("  ✅ Metrics endpoint: {response.status_code}")
        except Exception as e:
            health_results["metrics_endpoint"] = False
            print("  ❌ Metrics endpoint failed: {e}")

        # ChatOps endpoint
        try:
            response = requests.get(
                "http://{self.instance_ip}:{self.app_port}/chatops/status", timeout=10
            )
            health_results["chatops_endpoint"] = response.status_code == 200
            print("  ✅ ChatOps endpoint: {response.status_code}")
        except Exception as e:
            health_results["chatops_endpoint"] = False
            print("  ❌ ChatOps endpoint failed: {e}")

        return health_results

    def deploy(self) -> bool:
        """Main deployment method"""
        print("🚀 Starting Flask application deployment...")
        print("📍 Target instance: {self.instance_ip}")
        print("🔑 SSH key: {self.key_path}")

        try:
            # Step 1: Copy files
            if not self.copy_files_to_instance():
                return False

            # Step 2: Setup environment
            if not self.setup_environment():
                return False

            # Step 3: Deploy with Docker
            if not self.deploy_docker():
                return False

            # Step 4: Wait for service
            if not self.wait_for_service():
                return False

            # Step 5: Health checks
            health_results = self.run_health_checks()

            # Summary
            print("\n" + "=" * 50)
            print("🎉 DEPLOYMENT SUMMARY")
            print("=" * 50)
            print("📍 Instance: {self.instance_ip}")
            print("🌐 Application URL: http://{self.instance_ip}:{self.app_port}")
            print(
                "🏥 Health Status: {sum(" "health_results.values())}/{len(health_results)} endpoints healthy"
            )

            if all(health_results.values()):
                print("✅ All health checks passed! Deployment successful!")
                return True
            else:
                print("⚠️  Some health checks failed. Please investigate.")
                return False

        except Exception as e:
            print("❌ Deployment failed: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Deploy Flask ChatOps application")
    parser.add_argument("--instance-ip", required=True, help="EC2 instance public IP")
    parser.add_argument(
        "--key-path",
        default="~/.ssh/smartcloudops-ai-key.pem",
        help="SSH private key path",
    )

    args = parser.parse_args()

    deployer = FlaskAppDeployer(args.instance_ip, args.key_path)
    success = deployer.deploy()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

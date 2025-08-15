#!/usr/bin/env python3
"""
Load Testing Framework for Smart CloudOps AI
Phase 6.2: Load Testing & Performance Optimization
"""

import argparse
import asyncio
import json
import logging
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LoadTester:
    """Comprehensive load testing for Smart CloudOps AI Flask application."""

    def __init__(self, base_url: str = "http://localhost:3003"):
        self.base_url = base_url.rstrip("/")
        self.results = {
            "timestamp": "",
            "base_url": base_url,
            "test_scenarios": {},
            "performance_metrics": {},
            "bottlenecks": [],
            "recommendations": [],
        }

        # Test endpoints to load test
        self.endpoints = [
            "/",
            "/health",
            "/status",
            "/query",
            "/anomaly/status",
            "/metrics",
        ]

        # Load test scenarios
        self.scenarios = {
            "baseline": {
                "concurrent_users": 10,
                "requests_per_user": 50,
                "ramp_up_time": 10,
                "description": "Baseline performance test",
            },
            "normal_load": {
                "concurrent_users": 50,
                "requests_per_user": 100,
                "ramp_up_time": 30,
                "description": "Normal production load",
            },
            "peak_load": {
                "concurrent_users": 100,
                "requests_per_user": 200,
                "ramp_up_time": 60,
                "description": "Peak load simulation",
            },
        }

    async def test_endpoint(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        user_id: int,
        request_id: int,
    ) -> Dict[str, Any]:
        """Test a single endpoint and return performance metrics."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            # Prepare request data for POST endpoints
            if endpoint == "/query":
                data = {
                    "query": f"Test query from user {user_id} request {request_id}",
                    "context": "load_testing",
                }
                async with session.post(url, json=data) as response:
                    response_time = time.time() - start_time
                    return {
                        "endpoint": endpoint,
                        "user_id": user_id,
                        "request_id": request_id,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": response.status == 200,
                        "error": None,
                    }
            else:
                # GET request for other endpoints
                async with session.get(url) as response:
                    response_time = time.time() - start_time
                    return {
                        "endpoint": endpoint,
                        "user_id": user_id,
                        "request_id": request_id,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": response.status == 200,
                        "error": None,
                    }

        except Exception as e:
            response_time = time.time() - start_time
            return {
                "endpoint": endpoint,
                "user_id": user_id,
                "request_id": request_id,
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e),
            }

    async def simulate_user(
        self, session: aiohttp.ClientSession, user_id: int, scenario: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simulate a single user making multiple requests."""
        results = []
        requests_per_user = scenario["requests_per_user"]

        for request_id in range(requests_per_user):
            # Randomly select endpoint for variety
            import secrets

            # Security fix: Use secrets module for cryptographically secure randomness
            endpoint = secrets.choice(self.endpoints)

            result = await self.test_endpoint(session, endpoint, user_id, request_id)
            results.append(result)

            # Small delay between requests to simulate real user behavior
            await asyncio.sleep(0.1)

        return results

    async def run_scenario(
        self, scenario_name: str, scenario_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a specific load test scenario."""
        logger.info(f"🚀 Running scenario: {scenario_name}")
        logger.info(
            f"📊 Config: {scenario_config['concurrent_users']} users, "
            f"{scenario_config['requests_per_user']} requests/user"
        )

        start_time = time.time()
        all_results = []

        # Create connection pool
        connector = aiohttp.TCPConnector(limit=scenario_config["concurrent_users"] * 2)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            # Create tasks for all users
            tasks = []
            for user_id in range(scenario_config["concurrent_users"]):
                task = asyncio.create_task(
                    self.simulate_user(session, user_id, scenario_config)
                )
                tasks.append(task)

            # Execute all tasks concurrently
            user_results = await asyncio.gather(*tasks)

            # Flatten results
            for user_result in user_results:
                all_results.extend(user_result)

        end_time = time.time()
        total_time = end_time - start_time

        # Calculate metrics
        metrics = self._calculate_metrics(all_results, total_time, scenario_config)

        scenario_result = {
            "scenario_name": scenario_name,
            "config": scenario_config,
            "total_requests": len(all_results),
            "total_time": total_time,
            "results": all_results,
            "metrics": metrics,
        }

        self.results["test_scenarios"][scenario_name] = scenario_result
        logger.info(f"✅ Scenario {scenario_name} completed in {total_time:.2f}s")

        return scenario_result

    def _calculate_metrics(
        self,
        results: List[Dict[str, Any]],
        total_time: float,
        scenario_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        if not results:
            return {}

        # Response time metrics
        response_times = [r["response_time"] for r in results if r["success"]]
        error_count = len([r for r in results if not r["success"]])
        success_count = len(results) - error_count

        if not response_times:
            return {"error": "No successful requests to calculate metrics"}

        # Basic metrics
        metrics = {
            "total_requests": len(results),
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": (success_count / len(results)) * 100,
            "total_time": total_time,
            "requests_per_second": len(results) / total_time,
            "concurrent_users": scenario_config["concurrent_users"],
            "requests_per_user": scenario_config["requests_per_user"],
        }

        # Response time statistics
        metrics.update(
            {
                "response_time": {
                    "min": min(response_times),
                    "max": max(response_times),
                    "mean": statistics.mean(response_times),
                    "median": statistics.median(response_times),
                }
            }
        )

        return metrics

    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all load test scenarios."""
        logger.info("🚀 Starting comprehensive load testing")

        # Update timestamp
        self.results["timestamp"] = datetime.now().isoformat()

        # Run each scenario
        for scenario_name, scenario_config in self.scenarios.items():
            try:
                await self.run_scenario(scenario_name, scenario_config)
                # Small delay between scenarios
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"❌ Scenario {scenario_name} failed: {e}")
                self.results["test_scenarios"][scenario_name] = {
                    "error": str(e),
                    "status": "failed",
                }

        # Analyze overall performance
        self._analyze_performance()
        self._identify_bottlenecks()
        self._generate_recommendations()

        return self.results

    def _analyze_performance(self):
        """Analyze overall performance across all scenarios."""
        logger.info("📊 Analyzing overall performance...")

        overall_metrics = {
            "total_scenarios": len(self.scenarios),
            "successful_scenarios": 0,
            "total_requests": 0,
            "total_successful_requests": 0,
            "overall_success_rate": 0,
            "peak_rps": 0,
        }

        for scenario_name, scenario_result in self.results["test_scenarios"].items():
            if "error" not in scenario_result and "metrics" in scenario_result:
                overall_metrics["successful_scenarios"] += 1

                metrics = scenario_result["metrics"]

                # Safe metric extraction with defaults
                total_requests = metrics.get("total_requests", 0)
                successful_requests = metrics.get("successful_requests", 0)
                rps = metrics.get("requests_per_second", 0)

                overall_metrics["total_requests"] += total_requests
                overall_metrics["total_successful_requests"] += successful_requests

                if rps > overall_metrics["peak_rps"]:
                    overall_metrics["peak_rps"] = rps

        # Calculate success rate safely
        if overall_metrics["total_requests"] > 0:
            overall_metrics["overall_success_rate"] = (
                overall_metrics["total_successful_requests"]
                / overall_metrics["total_requests"]
            ) * 100
        else:
            overall_metrics["overall_success_rate"] = 0

        self.results["performance_metrics"] = overall_metrics

    def _identify_bottlenecks(self):
        """Identify performance bottlenecks."""
        logger.info("🔍 Identifying performance bottlenecks...")

        bottlenecks = []

        # Check for high error rates
        for scenario_name, scenario_result in self.results["test_scenarios"].items():
            if "error" not in scenario_result and "metrics" in scenario_result:
                metrics = scenario_result["metrics"]
                success_rate = metrics.get("success_rate", 0)
                if success_rate < 95:
                    bottlenecks.append(
                        {
                            "type": "high_error_rate",
                            "scenario": scenario_name,
                            "severity": "high" if success_rate < 80 else "medium",
                            "description": f"Success rate {success_rate:.1f}% is below 95% threshold",
                            "recommendation": "Investigate endpoint failures and improve error handling",
                        }
                    )

        # Check for slow response times
        for scenario_name, scenario_result in self.results["test_scenarios"].items():
            if "error" not in scenario_result and "metrics" in scenario_result:
                metrics = scenario_result["metrics"]
                response_time_data = metrics.get("response_time", {})
                avg_response_time = response_time_data.get("mean", 0)

                if avg_response_time > 2.0:  # 2 seconds threshold
                    bottlenecks.append(
                        {
                            "type": "slow_response_time",
                            "scenario": scenario_name,
                            "severity": "high" if avg_response_time > 5.0 else "medium",
                            "description": f"Average response time {avg_response_time:.2f}s exceeds 2s threshold",
                            "recommendation": "Optimize slow endpoints and consider caching strategies",
                        }
                    )

        self.results["bottlenecks"] = bottlenecks

    def _generate_recommendations(self):
        """Generate performance optimization recommendations."""
        logger.info("💡 Generating performance recommendations...")

        recommendations = []

        # Based on bottlenecks
        for bottleneck in self.results["bottlenecks"]:
            recommendations.append(
                {
                    "priority": bottleneck["severity"].upper(),
                    "category": bottleneck["type"],
                    "description": bottleneck["recommendation"],
                    "scenario": bottleneck["scenario"],
                }
            )

        # General recommendations
        recommendations.extend(
            [
                {
                    "priority": "MEDIUM",
                    "category": "monitoring",
                    "description": "Implement real-time performance monitoring and alerting",
                    "scenario": "all",
                },
                {
                    "priority": "LOW",
                    "category": "caching",
                    "description": "Consider implementing Redis caching for frequently accessed data",
                    "scenario": "all",
                },
            ]
        )

        self.results["recommendations"] = recommendations

    def generate_report(self, output_file: str = None) -> str:
        """Generate a comprehensive load testing report."""
        if output_file is None:
            output_file = (
                Path(__file__).parent.parent / "docs" / "LOAD_TESTING_REPORT.md"
            )

        report = f"""# Load Testing Report - Smart CloudOps AI

**Generated**: {self.results['timestamp']}  
**Base URL**: {self.results['base_url']}

## 📊 Executive Summary

**Overall Performance Score**: {self.results['performance_metrics'].get('overall_success_rate', 0):.1f}%  
**Peak Throughput**: {self.results['performance_metrics'].get('peak_rps', 0):.1f} RPS  
**Total Requests**: {self.results['performance_metrics'].get('total_requests', 0):,}  
**Successful Scenarios**: {self.results['performance_metrics'].get('successful_scenarios', 0)}/{self.results['performance_metrics'].get('total_scenarios', 0)}

## 🚀 Test Scenarios

"""

        for scenario_name, scenario_result in self.results["test_scenarios"].items():
            if "error" in scenario_result:
                report += f"### {scenario_name.replace('_', ' ').title()}\n"
                report += f"**Status**: ❌ Failed\n"
                report += f"**Error**: {scenario_result['error']}\n\n"
            else:
                metrics = scenario_result["metrics"]
                report += f"### {scenario_name.replace('_', ' ').title()}\n"
                report += f"**Status**: ✅ Completed\n"
                report += f"**Total Requests**: {metrics.get('total_requests', 0):,}\n"
                report += f"**Success Rate**: {metrics.get('success_rate', 0):.1f}%\n"
                report += (
                    f"**Throughput**: {metrics.get('requests_per_second', 0):.1f} RPS\n"
                )
                report += f"**Avg Response Time**: {metrics.get('response_time', {}).get('mean', 0):.3f}s\n\n"

        # Bottlenecks section
        if self.results["bottlenecks"]:
            report += "## 🚨 Performance Bottlenecks\n\n"
            for bottleneck in self.results["bottlenecks"]:
                report += f"### {bottleneck['type'].replace('_', ' ').title()}\n"
                report += f"**Severity**: {bottleneck['severity'].upper()}\n"
                report += f"**Scenario**: {bottleneck['scenario']}\n"
                report += f"**Description**: {bottleneck['description']}\n"
                report += f"**Recommendation**: {bottleneck['recommendation']}\n\n"

        # Recommendations section
        if self.results["recommendations"]:
            report += "## 💡 Recommendations\n\n"
            for rec in self.results["recommendations"]:
                report += f"### {rec['priority']} Priority\n"
                report += f"**Category**: {rec['category']}\n"
                report += f"**Description**: {rec['description']}\n"
                report += f"**Scope**: {rec['scenario']}\n\n"

        report += "---\n\n**Note**: This report was generated automatically from load testing results. "
        report += (
            "Review all bottlenecks and recommendations before production deployment."
        )

        # Write report to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(report)

        logger.info(f"Load testing report generated: {output_file}")
        return str(output_file)


async def main():
    """Main function to run load testing."""
    parser = argparse.ArgumentParser(description="Load Testing for Smart CloudOps AI")
    parser.add_argument(
        "--url",
        default="http://localhost:5000",
        help="Base URL to test (default: http://localhost:5000)",
    )
    parser.add_argument(
        "--scenarios", nargs="+", help="Specific scenarios to run (default: all)"
    )

    args = parser.parse_args()

    try:
        # Initialize load tester
        load_tester = LoadTester(args.url)

        # Filter scenarios if specified
        if args.scenarios:
            filtered_scenarios = {}
            for scenario_name in args.scenarios:
                if scenario_name in load_tester.scenarios:
                    filtered_scenarios[scenario_name] = load_tester.scenarios[
                        scenario_name
                    ]
                else:
                    logger.warning(f"Unknown scenario: {scenario_name}")

            if filtered_scenarios:
                load_tester.scenarios = filtered_scenarios
            else:
                logger.error("No valid scenarios specified")
                return

        # Run load testing
        results = await load_tester.run_all_scenarios()

        # Generate report
        report_path = load_tester.generate_report()

        # Print summary
        print(f"\n🚀 Load Testing Complete!")
        print(
            f"📊 Overall Success Rate: {results['performance_metrics'].get('overall_success_rate', 0):.1f}%"
        )
        print(
            f"⚡ Peak Throughput: {results['performance_metrics'].get('peak_rps', 0):.1f} RPS"
        )
        print(f"📋 Report Generated: {report_path}")

        # Print bottlenecks
        if results["bottlenecks"]:
            print(f"\n🚨 Performance Bottlenecks Found: {len(results['bottlenecks'])}")
            for bottleneck in results["bottlenecks"][:3]:  # Show first 3
                print(f"  - {bottleneck['type']}: {bottleneck['description']}")

        # Exit with error code if critical issues found
        critical_bottlenecks = [
            b for b in results["bottlenecks"] if b["severity"] == "high"
        ]
        if critical_bottlenecks:
            print(
                f"\n❌ {len(critical_bottlenecks)} critical performance issues found."
            )
            sys.exit(1)
        else:
            print(f"\n✅ Load testing completed successfully.")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⏹️ Load testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Load testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
SmartCloudOps AI - Performance Analysis and Optimization
Automated performance profiling, bottleneck identification, and tuning recommendations
"""

import json
import os
import sqlite3
import statistics
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil
import requests

# Add app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app"))


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""

    timestamp: float
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]


@dataclass
class PerformanceSample:
    """Complete performance sample"""

    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    open_files: int
    threads: int
    response_times: List[float]
    error_count: int
    request_count: int


class PerformanceMonitor:
    """Real-time performance monitoring and analysis"""

    def __init__(self, app_url: str = "http://localhost:5000"):
        self.app_url = app_url
        self.samples: List[PerformanceSample] = []
        self.is_monitoring = False
        self.monitor_thread = None
        self.start_time = None

        # Performance thresholds
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "response_time_p95": 1000.0,  # ms
            "error_rate": 1.0,  # percentage
            "disk_io_mb_per_sec": 100.0,
            "network_mb_per_sec": 50.0,
        }

        # Initialize database for storing results
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for performance data"""
        os.makedirs("docs/results", exist_ok=True)
        self.db_path = "docs/results/performance_data.db"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                cpu_percent REAL,
                memory_mb REAL,
                memory_percent REAL,
                disk_io_read_mb REAL,
                disk_io_write_mb REAL,
                network_sent_mb REAL,
                network_recv_mb REAL,
                open_files INTEGER,
                threads INTEGER,
                avg_response_time REAL,
                p95_response_time REAL,
                error_count INTEGER,
                request_count INTEGER,
                test_session TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT,
                start_time REAL,
                end_time REAL,
                duration_seconds REAL,
                total_requests INTEGER,
                total_errors INTEGER,
                avg_response_time REAL,
                p95_response_time REAL,
                p99_response_time REAL,
                max_cpu_percent REAL,
                avg_memory_mb REAL,
                peak_memory_mb REAL,
                bottlenecks TEXT,
                recommendations TEXT,
                baseline BOOLEAN DEFAULT 0
            )
        """
        )

        conn.commit()
        conn.close()

    def start_monitoring(self, duration_seconds: Optional[int] = None):
        """Start performance monitoring"""
        self.is_monitoring = True
        self.start_time = time.time()
        self.samples.clear()

        print(
            f"🔍 Starting performance monitoring for {duration_seconds or 'unlimited'} seconds..."
        )

        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, args=(duration_seconds,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        print(
            f"⏹️ Performance monitoring stopped. Collected {len(self.samples)} samples."
        )

    def _monitor_loop(self, duration_seconds: Optional[int]):
        """Main monitoring loop"""
        start_time = time.time()
        sample_interval = 1.0  # 1 second intervals

        while self.is_monitoring:
            if duration_seconds and (time.time() - start_time) >= duration_seconds:
                break

            try:
                sample = self._collect_sample()
                self.samples.append(sample)

                # Store in database
                self._store_sample(sample)

                # Check for critical issues
                self._check_critical_thresholds(sample)

            except Exception as e:
                print(f"⚠️ Error collecting performance sample: {e}")

            time.sleep(sample_interval)

        self.is_monitoring = False

    def _collect_sample(self) -> PerformanceSample:
        """Collect a single performance sample"""
        timestamp = time.time()

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()

        # Process metrics (if we can find the app process)
        open_files = 0
        threads = 0
        try:
            current_process = psutil.Process()
            open_files = (
                current_process.num_fds() if hasattr(current_process, "num_fds") else 0
            )
            threads = current_process.num_threads()
        except:
            pass

        # Application metrics via HTTP
        response_times = []
        error_count = 0
        request_count = 0

        try:
            # Test multiple endpoints for response time
            endpoints = ["/health", "/metrics", "/observability/health"]

            for endpoint in endpoints:
                start = time.time()
                try:
                    response = requests.get(f"{self.app_url}{endpoint}", timeout=5)
                    response_time = (time.time() - start) * 1000  # ms
                    response_times.append(response_time)
                    request_count += 1

                    if response.status_code >= 400:
                        error_count += 1

                except requests.RequestException:
                    error_count += 1
                    request_count += 1
        except:
            pass

        return PerformanceSample(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_mb=memory.used / 1024 / 1024,
            memory_percent=memory.percent,
            disk_io_read_mb=(disk_io.read_bytes / 1024 / 1024) if disk_io else 0,
            disk_io_write_mb=(disk_io.write_bytes / 1024 / 1024) if disk_io else 0,
            network_sent_mb=(network_io.bytes_sent / 1024 / 1024) if network_io else 0,
            network_recv_mb=(network_io.bytes_recv / 1024 / 1024) if network_io else 0,
            open_files=open_files,
            threads=threads,
            response_times=response_times,
            error_count=error_count,
            request_count=request_count,
        )

    def _store_sample(self, sample: PerformanceSample):
        """Store sample in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        avg_response_time = (
            statistics.mean(sample.response_times) if sample.response_times else 0
        )
        p95_response_time = (
            statistics.quantiles(sample.response_times, n=20)[18]
            if len(sample.response_times) >= 5
            else avg_response_time
        )

        cursor.execute(
            """
            INSERT INTO performance_samples (
                timestamp, cpu_percent, memory_mb, memory_percent,
                disk_io_read_mb, disk_io_write_mb, network_sent_mb, network_recv_mb,
                open_files, threads, avg_response_time, p95_response_time,
                error_count, request_count, test_session
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                sample.timestamp,
                sample.cpu_percent,
                sample.memory_mb,
                sample.memory_percent,
                sample.disk_io_read_mb,
                sample.disk_io_write_mb,
                sample.network_sent_mb,
                sample.network_recv_mb,
                sample.open_files,
                sample.threads,
                avg_response_time,
                p95_response_time,
                sample.error_count,
                sample.request_count,
                self.start_time,
            ),
        )

        conn.commit()
        conn.close()

    def _check_critical_thresholds(self, sample: PerformanceSample):
        """Check for critical performance issues"""
        issues = []

        if sample.cpu_percent > self.thresholds["cpu_percent"]:
            issues.append(f"High CPU usage: {sample.cpu_percent:.1f}%")

        if sample.memory_percent > self.thresholds["memory_percent"]:
            issues.append(f"High memory usage: {sample.memory_percent:.1f}%")

        if sample.response_times:
            avg_response = statistics.mean(sample.response_times)
            if avg_response > self.thresholds["response_time_p95"]:
                issues.append(f"Slow response time: {avg_response:.1f}ms")

        if sample.request_count > 0:
            error_rate = (sample.error_count / sample.request_count) * 100
            if error_rate > self.thresholds["error_rate"]:
                issues.append(f"High error rate: {error_rate:.1f}%")

        if issues:
            print(f"⚠️ Performance issues detected: {', '.join(issues)}")

    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze collected performance data"""
        if not self.samples:
            return {"error": "No performance data available"}

        print("📊 Analyzing performance data...")

        # Calculate statistics
        cpu_values = [s.cpu_percent for s in self.samples]
        memory_values = [s.memory_mb for s in self.samples]
        memory_percent_values = [s.memory_percent for s in self.samples]

        # Response time analysis
        all_response_times = []
        total_requests = 0
        total_errors = 0

        for sample in self.samples:
            all_response_times.extend(sample.response_times)
            total_requests += sample.request_count
            total_errors += sample.error_count

        # Calculate percentiles
        response_percentiles = {}
        if all_response_times:
            sorted_times = sorted(all_response_times)
            response_percentiles = {
                "p50": statistics.median(sorted_times),
                "p95": (
                    statistics.quantiles(sorted_times, n=20)[18]
                    if len(sorted_times) >= 5
                    else statistics.median(sorted_times)
                ),
                "p99": (
                    statistics.quantiles(sorted_times, n=100)[98]
                    if len(sorted_times) >= 10
                    else statistics.median(sorted_times)
                ),
                "avg": statistics.mean(sorted_times),
                "max": max(sorted_times),
            }

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks()

        # Generate recommendations
        recommendations = self._generate_recommendations()

        analysis = {
            "test_duration": len(self.samples),
            "sample_count": len(self.samples),
            "cpu_stats": {
                "avg": statistics.mean(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
                "p95": (
                    statistics.quantiles(cpu_values, n=20)[18]
                    if len(cpu_values) >= 5
                    else max(cpu_values)
                ),
            },
            "memory_stats": {
                "avg_mb": statistics.mean(memory_values),
                "peak_mb": max(memory_values),
                "avg_percent": statistics.mean(memory_percent_values),
                "peak_percent": max(memory_percent_values),
            },
            "response_time_stats": response_percentiles,
            "request_stats": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": (
                    (total_errors / total_requests * 100) if total_requests > 0 else 0
                ),
                "avg_rps": total_requests / len(self.samples) if self.samples else 0,
            },
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
            "thresholds_exceeded": self._check_threshold_violations(),
        }

        # Store test results
        self._store_test_results(analysis)

        return analysis

    def _identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        if not self.samples:
            return bottlenecks

        # CPU bottleneck
        cpu_values = [s.cpu_percent for s in self.samples]
        avg_cpu = statistics.mean(cpu_values)
        if avg_cpu > 70:
            bottlenecks.append(f"CPU bound - Average {avg_cpu:.1f}% usage")

        # Memory bottleneck
        memory_percent_values = [s.memory_percent for s in self.samples]
        avg_memory = statistics.mean(memory_percent_values)
        if avg_memory > 80:
            bottlenecks.append(f"Memory constrained - Average {avg_memory:.1f}% usage")

        # Response time bottleneck
        all_response_times = []
        for sample in self.samples:
            all_response_times.extend(sample.response_times)

        if all_response_times:
            avg_response = statistics.mean(all_response_times)
            if avg_response > 500:  # 500ms threshold
                bottlenecks.append(
                    f"Slow response times - Average {avg_response:.1f}ms"
                )

        # Database/IO bottleneck (inferred from slow responses + normal CPU)
        if all_response_times and avg_cpu < 50:
            p95_response = (
                statistics.quantiles(sorted(all_response_times), n=20)[18]
                if len(all_response_times) >= 5
                else avg_response
            )
            if p95_response > 1000:  # 1 second
                bottlenecks.append(
                    "Potential database/IO bottleneck - slow responses with low CPU"
                )

        # Threading bottleneck
        thread_counts = [s.threads for s in self.samples if s.threads > 0]
        if thread_counts:
            avg_threads = statistics.mean(thread_counts)
            if avg_threads > 100:
                bottlenecks.append(
                    f"High thread count - Average {avg_threads:.0f} threads"
                )

        return bottlenecks

    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if not self.samples:
            return recommendations

        # CPU recommendations
        cpu_values = [s.cpu_percent for s in self.samples]
        avg_cpu = statistics.mean(cpu_values)

        if avg_cpu > 80:
            recommendations.append(
                "Scale horizontally or optimize CPU-intensive operations"
            )
        elif avg_cpu > 60:
            recommendations.append("Consider CPU optimization for peak load handling")

        # Memory recommendations
        memory_percent_values = [s.memory_percent for s in self.samples]
        avg_memory = statistics.mean(memory_percent_values)

        if avg_memory > 85:
            recommendations.append(
                "Increase memory allocation or optimize memory usage"
            )
        elif avg_memory > 70:
            recommendations.append(
                "Monitor memory growth and consider caching optimizations"
            )

        # Response time recommendations
        all_response_times = []
        for sample in self.samples:
            all_response_times.extend(sample.response_times)

        if all_response_times:
            avg_response = statistics.mean(all_response_times)
            if avg_response > 1000:
                recommendations.append("Optimize database queries and add caching")
            elif avg_response > 500:
                recommendations.append(
                    "Review API endpoint performance and add indices"
                )

        # Error rate recommendations
        total_requests = sum(s.request_count for s in self.samples)
        total_errors = sum(s.error_count for s in self.samples)
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0

        if error_rate > 5:
            recommendations.append("Investigate and fix high error rate issues")
        elif error_rate > 1:
            recommendations.append("Monitor error patterns and improve error handling")

        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("Performance is within acceptable thresholds")
            recommendations.append("Consider load testing with higher concurrent users")

        return recommendations

    def _check_threshold_violations(self) -> Dict[str, Any]:
        """Check which thresholds were exceeded"""
        violations = {}

        if not self.samples:
            return violations

        # Check each threshold
        cpu_values = [s.cpu_percent for s in self.samples]
        max_cpu = max(cpu_values)
        violations["cpu_percent"] = {
            "threshold": self.thresholds["cpu_percent"],
            "max_value": max_cpu,
            "exceeded": max_cpu > self.thresholds["cpu_percent"],
        }

        memory_percent_values = [s.memory_percent for s in self.samples]
        max_memory = max(memory_percent_values)
        violations["memory_percent"] = {
            "threshold": self.thresholds["memory_percent"],
            "max_value": max_memory,
            "exceeded": max_memory > self.thresholds["memory_percent"],
        }

        # Response time
        all_response_times = []
        for sample in self.samples:
            all_response_times.extend(sample.response_times)

        if all_response_times:
            p95_response = (
                statistics.quantiles(sorted(all_response_times), n=20)[18]
                if len(all_response_times) >= 5
                else max(all_response_times)
            )
            violations["response_time_p95"] = {
                "threshold": self.thresholds["response_time_p95"],
                "max_value": p95_response,
                "exceeded": p95_response > self.thresholds["response_time_p95"],
            }

        return violations

    def _store_test_results(self, analysis: Dict[str, Any]):
        """Store test results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        duration = analysis["test_duration"]
        cpu_stats = analysis["cpu_stats"]
        memory_stats = analysis["memory_stats"]
        response_stats = analysis.get("response_time_stats", {})
        request_stats = analysis["request_stats"]

        cursor.execute(
            """
            INSERT INTO performance_tests (
                test_name, start_time, end_time, duration_seconds,
                total_requests, total_errors, avg_response_time,
                p95_response_time, p99_response_time, max_cpu_percent,
                avg_memory_mb, peak_memory_mb, bottlenecks, recommendations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                f"performance_test_{int(self.start_time)}",
                self.start_time,
                time.time(),
                duration,
                request_stats["total_requests"],
                request_stats["total_errors"],
                response_stats.get("avg", 0),
                response_stats.get("p95", 0),
                response_stats.get("p99", 0),
                cpu_stats["max"],
                memory_stats["avg_mb"],
                memory_stats["peak_mb"],
                json.dumps(analysis["bottlenecks"]),
                json.dumps(analysis["recommendations"]),
            ),
        )

        conn.commit()
        conn.close()

    def generate_report(self, analysis: Dict[str, Any], output_file: str = None):
        """Generate a detailed performance report"""
        if not output_file:
            output_file = f"docs/results/performance_report_{int(time.time())}.md"

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        report = f"""# 📊 Performance Analysis Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Test Duration**: {analysis['test_duration']} seconds  
**Samples Collected**: {analysis['sample_count']}

## 🎯 Executive Summary

"""

        # Add threshold status
        violations = analysis.get("thresholds_exceeded", {})
        critical_issues = sum(
            1
            for v in violations.values()
            if isinstance(v, dict) and v.get("exceeded", False)
        )

        if critical_issues == 0:
            report += "✅ **Status**: All performance thresholds met\n\n"
        else:
            report += (
                f"⚠️ **Status**: {critical_issues} performance threshold(s) exceeded\n\n"
            )

        # CPU Performance
        cpu_stats = analysis.get("cpu_stats", {})
        report += f"""## 🖥️ CPU Performance

- **Average**: {cpu_stats.get('avg', 0):.1f}%
- **Peak**: {cpu_stats.get('max', 0):.1f}%
- **95th Percentile**: {cpu_stats.get('p95', 0):.1f}%

"""

        # Memory Performance
        memory_stats = analysis.get("memory_stats", {})
        report += f"""## 🧠 Memory Performance

- **Average Usage**: {memory_stats.get('avg_mb', 0):.0f} MB ({memory_stats.get('avg_percent', 0):.1f}%)
- **Peak Usage**: {memory_stats.get('peak_mb', 0):.0f} MB ({memory_stats.get('peak_percent', 0):.1f}%)

"""

        # Response Time Performance
        response_stats = analysis.get("response_time_stats", {})
        if response_stats:
            report += f"""## ⚡ Response Time Performance

- **Average**: {response_stats.get('avg', 0):.1f}ms
- **Median (P50)**: {response_stats.get('p50', 0):.1f}ms
- **95th Percentile**: {response_stats.get('p95', 0):.1f}ms
- **99th Percentile**: {response_stats.get('p99', 0):.1f}ms
- **Maximum**: {response_stats.get('max', 0):.1f}ms

"""

        # Request Statistics
        request_stats = analysis.get("request_stats", {})
        report += f"""## 📈 Request Statistics

- **Total Requests**: {request_stats.get('total_requests', 0):,}
- **Total Errors**: {request_stats.get('total_errors', 0):,}
- **Error Rate**: {request_stats.get('error_rate', 0):.2f}%
- **Average RPS**: {request_stats.get('avg_rps', 0):.1f}

"""

        # Bottlenecks
        bottlenecks = analysis.get("bottlenecks", [])
        if bottlenecks:
            report += "## 🚨 Identified Bottlenecks\n\n"
            for bottleneck in bottlenecks:
                report += f"- {bottleneck}\n"
            report += "\n"

        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            report += "## 💡 Optimization Recommendations\n\n"
            for i, recommendation in enumerate(recommendations, 1):
                report += f"{i}. {recommendation}\n"
            report += "\n"

        # Threshold Analysis
        if violations:
            report += "## 🎯 Threshold Analysis\n\n"
            report += "| Metric | Threshold | Max Value | Status |\n"
            report += "|--------|-----------|-----------|--------|\n"

            for metric, data in violations.items():
                if isinstance(data, dict):
                    status = "❌ EXCEEDED" if data.get("exceeded") else "✅ OK"
                    threshold = data.get("threshold", "N/A")
                    max_value = data.get("max_value", "N/A")

                    # Format values based on metric type
                    if "percent" in metric:
                        threshold = f"{threshold}%"
                        max_value = f"{max_value:.1f}%"
                    elif "time" in metric:
                        threshold = f"{threshold}ms"
                        max_value = f"{max_value:.1f}ms"

                    report += f"| {metric.replace('_', ' ').title()} | {threshold} | {max_value} | {status} |\n"
            report += "\n"

        # Save report
        with open(output_file, "w") as f:
            f.write(report)

        print(f"📄 Performance report saved to: {output_file}")
        return output_file


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="SmartCloudOps AI Performance Analyzer"
    )
    parser.add_argument(
        "--url", default="http://localhost:5000", help="Application URL"
    )
    parser.add_argument(
        "--duration", type=int, default=60, help="Monitoring duration in seconds"
    )
    parser.add_argument("--output", help="Output report file")

    args = parser.parse_args()

    monitor = PerformanceMonitor(args.url)

    try:
        monitor.start_monitoring(args.duration)

        # Wait for monitoring to complete
        while monitor.is_monitoring:
            time.sleep(1)

        # Analyze results
        analysis = monitor.analyze_performance()

        # Generate report
        report_file = monitor.generate_report(analysis, args.output)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE ANALYSIS COMPLETE")
        print("=" * 60)

        cpu_stats = analysis.get("cpu_stats", {})
        memory_stats = analysis.get("memory_stats", {})
        response_stats = analysis.get("response_time_stats", {})

        print(
            f"🖥️ CPU: Avg {cpu_stats.get('avg', 0):.1f}% | Peak {cpu_stats.get('max', 0):.1f}%"
        )
        print(
            f"🧠 Memory: Avg {memory_stats.get('avg_percent', 0):.1f}% | Peak {memory_stats.get('peak_percent', 0):.1f}%"
        )

        if response_stats:
            print(
                f"⚡ Response: Avg {response_stats.get('avg', 0):.1f}ms | P95 {response_stats.get('p95', 0):.1f}ms"
            )

        bottlenecks = analysis.get("bottlenecks", [])
        if bottlenecks:
            print(f"\n🚨 Bottlenecks: {len(bottlenecks)} identified")
            for bottleneck in bottlenecks[:3]:  # Show first 3
                print(f"   • {bottleneck}")

        print(f"\n📄 Full report: {report_file}")

    except KeyboardInterrupt:
        print("\n⏹️ Monitoring interrupted by user")
        monitor.stop_monitoring()
    except Exception as e:
        print(f"❌ Error during performance analysis: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Jarvis AI Assistant - Health Monitor
Monitors the health of the Jarvis application and provides status information.
"""

import os
import sys
import time
import json
import psutil
import requests
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

class HealthMonitor:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.db_path = self.base_dir / 'jarvis.db'
        self.log_path = self.base_dir / 'logs' / 'jarvis.log'
        self.health_data = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'checks': {}
        }

    def check_database(self):
        """Check database connectivity and integrity"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Check if essential tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            required_tables = ['sys_command', 'web_command', 'events', 'reminders', 'notes']
            missing_tables = [t for t in required_tables if t not in tables]

            if missing_tables:
                self.health_data['checks']['database'] = {
                    'status': 'error',
                    'message': f'Missing tables: {missing_tables}'
                }
                return False

            # Test basic query
            cursor.execute("SELECT COUNT(*) FROM sys_command")
            count = cursor.fetchone()[0]

            conn.close()

            self.health_data['checks']['database'] = {
                'status': 'healthy',
                'message': f'Database accessible, {len(tables)} tables found'
            }
            return True

        except Exception as e:
            self.health_data['checks']['database'] = {
                'status': 'error',
                'message': f'Database error: {str(e)}'
            }
            return False

    def check_web_server(self):
        """Check if the web server is responsive"""
        try:
            response = requests.get('http://localhost:8000', timeout=5)
            if response.status_code == 200:
                self.health_data['checks']['web_server'] = {
                    'status': 'healthy',
                    'message': 'Web server responding'
                }
                return True
            else:
                self.health_data['checks']['web_server'] = {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}'
                }
                return False
        except requests.exceptions.ConnectionError:
            self.health_data['checks']['web_server'] = {
                'status': 'error',
                'message': 'Connection refused'
            }
            return False
        except Exception as e:
            self.health_data['checks']['web_server'] = {
                'status': 'error',
                'message': f'Error: {str(e)}'
            }
            return False

    def check_file_system(self):
        """Check if essential files and directories exist"""
        try:
            required_paths = [
                self.base_dir / 'main.py',
                self.base_dir / 'backend' / 'feature.py',
                self.base_dir / 'backend' / 'calendar.py',
                self.base_dir / 'backend' / 'notes.py',
                self.base_dir / 'frontend' / 'index.html'
            ]

            missing_paths = []
            for path in required_paths:
                if not path.exists():
                    missing_paths.append(str(path.relative_to(self.base_dir)))

            # Check logs directory
            logs_dir = self.base_dir / 'logs'
            if not logs_dir.exists():
                logs_dir.mkdir(exist_ok=True)

            if missing_paths:
                self.health_data['checks']['file_system'] = {
                    'status': 'error',
                    'message': f'Missing files: {missing_paths}'
                }
                return False

            self.health_data['checks']['file_system'] = {
                'status': 'healthy',
                'message': 'All essential files present'
            }
            return True

        except Exception as e:
            self.health_data['checks']['file_system'] = {
                'status': 'error',
                'message': f'File system error: {str(e)}'
            }
            return False

    def check_dependencies(self):
        """Check if required Python packages are installed"""
        try:
            with open(self.base_dir / 'requirements.txt', 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            missing_packages = []
            for req in requirements:
                package_name = req.split('==')[0].replace('-', '_')
                try:
                    __import__(package_name)
                except ImportError:
                    missing_packages.append(package_name)

            if missing_packages:
                self.health_data['checks']['dependencies'] = {
                    'status': 'warning',
                    'message': f'Missing packages: {missing_packages}'
                }
                return False

            self.health_data['checks']['dependencies'] = {
                'status': 'healthy',
                'message': 'All dependencies satisfied'
            }
            return True

        except Exception as e:
            self.health_data['checks']['dependencies'] = {
                'status': 'error',
                'message': f'Dependency check error: {str(e)}'
            }
            return False

    def check_system_resources(self):
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(self.base_dir))

            resource_data = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }

            # Determine status based on thresholds
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 95:
                status = 'critical'
            elif cpu_percent > 75 or memory.percent > 75 or disk.percent > 85:
                status = 'warning'
            else:
                status = 'healthy'

            self.health_data['checks']['system_resources'] = {
                'status': status,
                'data': resource_data,
                'message': f'CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%'
            }

            return status != 'critical'

        except Exception as e:
            self.health_data['checks']['system_resources'] = {
                'status': 'error',
                'message': f'Resource check error: {str(e)}'
            }
            return False

    def check_recent_activity(self):
        """Check if the application has been recently active"""
        try:
            # Check log file modification time
            if self.log_path.exists():
                log_mtime = datetime.fromtimestamp(self.log_path.stat().st_mtime)
                time_since_log = datetime.now() - log_mtime

                if time_since_log > timedelta(hours=1):
                    self.health_data['checks']['recent_activity'] = {
                        'status': 'warning',
                        'message': f'No log activity for {time_since_log}'
                    }
                else:
                    self.health_data['checks']['recent_activity'] = {
                        'status': 'healthy',
                        'message': f'Last log activity: {log_mtime.strftime("%Y-%m-%d %H:%M:%S")}'
                    }
            else:
                self.health_data['checks']['recent_activity'] = {
                    'status': 'warning',
                    'message': 'Log file not found'
                }

            return True

        except Exception as e:
            self.health_data['checks']['recent_activity'] = {
                'status': 'error',
                'message': f'Activity check error: {str(e)}'
            }
            return False

    def run_all_checks(self):
        """Run all health checks"""
        print("Running Jarvis Health Monitor...")
        print("=" * 50)

        checks = [
            ('Database', self.check_database),
            ('Web Server', self.check_web_server),
            ('File System', self.check_file_system),
            ('Dependencies', self.check_dependencies),
            ('System Resources', self.check_system_resources),
            ('Recent Activity', self.check_recent_activity)
        ]

        all_healthy = True
        for check_name, check_func in checks:
            print(f"Checking {check_name}...", end=" ")
            try:
                result = check_func()
                status = self.health_data['checks'][check_name.lower().replace(' ', '_')]['status']
                print(f"✅ {status.upper()}")
                if status in ['error', 'critical']:
                    all_healthy = False
            except Exception as e:
                print(f"❌ ERROR: {e}")
                all_healthy = False

        # Overall status
        overall_status = 'healthy' if all_healthy else 'unhealthy'
        self.health_data['status'] = overall_status

        print("=" * 50)
        print(f"Overall Status: {overall_status.upper()}")

        return self.health_data

    def generate_report(self):
        """Generate a detailed health report"""
        self.run_all_checks()

        report = {
            'health_check': self.health_data,
            'summary': {
                'total_checks': len(self.health_data['checks']),
                'healthy_checks': len([c for c in self.health_data['checks'].values() if c['status'] == 'healthy']),
                'warning_checks': len([c for c in self.health_data['checks'].values() if c['status'] == 'warning']),
                'error_checks': len([c for c in self.health_data['checks'].values() if c['status'] in ['error', 'critical']])
            }
        }

        return report

    def save_report(self, filename=None):
        """Save health report to file"""
        if filename is None:
            filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = self.generate_report()
        report_path = self.base_dir / 'logs' / filename

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Health report saved to: {report_path}")
        return report_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Jarvis Health Monitor')
    parser.add_argument('--output', '-o', help='Output file for health report')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--watch', '-w', action='store_true', help='Monitor continuously')
    parser.add_argument('--interval', '-i', type=int, default=60, help='Watch interval in seconds')

    args = parser.parse_args()

    monitor = HealthMonitor()

    if args.json:
        report = monitor.generate_report()
        print(json.dumps(report, indent=2))
    elif args.watch:
        try:
            while True:
                monitor.run_all_checks()
                print(f"\nWaiting {args.interval} seconds... (Ctrl+C to stop)")
                time.sleep(args.interval)
                print("\n" + "=" * 50)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    else:
        monitor.run_all_checks()

        if args.output:
            monitor.save_report(args.output)
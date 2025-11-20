#!/usr/bin/env python3
"""
Jarvis AI Assistant - Auto Restart Monitor
Monitors the Jarvis application and restarts it if it crashes or becomes unresponsive.
"""

import os
import sys
import time
import psutil
import requests
import subprocess
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from health_monitor import HealthMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_restart.log'),
        logging.StreamHandler()
    ]
)

class AutoRestartMonitor:
    def __init__(self, max_restart_attempts=3, restart_delay=30, check_interval=60):
        self.max_restart_attempts = max_restart_attempts
        self.restart_delay = restart_delay
        self.check_interval = check_interval
        self.base_dir = Path(__file__).parent.parent
        self.restart_count = 0
        self.last_restart_time = None
        self.health_monitor = HealthMonitor()

    def is_jarvis_running(self):
        """Check if Jarvis main process is running"""
        try:
            # Look for Python processes running main.py
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['cmdline'] and len(proc.info['cmdline']) > 1:
                    if 'python' in proc.info['cmdline'][0] and 'main.py' in ' '.join(proc.info['cmdline']):
                        return True, proc.info['pid']
            return False, None
        except Exception as e:
            logging.error(f"Error checking if Jarvis is running: {e}")
            return False, None

    def is_jarvis_responsive(self):
        """Check if Jarvis web interface is responsive"""
        try:
            response = requests.get('http://localhost:8000', timeout=10)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        except Exception as e:
            logging.error(f"Error checking Jarvis responsiveness: {e}")
            return False

    def start_jarvis(self):
        """Start Jarvis application"""
        try:
            logging.info("Starting Jarvis application...")

            # Change to application directory
            os.chdir(str(self.base_dir))

            # Start the process
            process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            logging.info(f"Jarvis started with PID: {process.pid}")

            # Give it time to start up
            time.sleep(10)

            # Check if it's still running
            if process.poll() is None:
                self.restart_count += 1
                self.last_restart_time = datetime.now()

                # Log the restart
                self.log_restart()

                return True, process.pid
            else:
                stdout, stderr = process.communicate()
                logging.error(f"Jarvis failed to start. Return code: {process.returncode}")
                logging.error(f"Stdout: {stdout}")
                logging.error(f"Stderr: {stderr}")
                return False, None

        except Exception as e:
            logging.error(f"Error starting Jarvis: {e}")
            return False, None

    def stop_jarvis(self):
        """Gracefully stop Jarvis application"""
        try:
            running, pid = self.is_jarvis_running()
            if running and pid:
                logging.info(f"Stopping Jarvis with PID: {pid}")

                # Try graceful shutdown first
                process = psutil.Process(pid)
                process.terminate()

                # Wait for process to terminate
                try:
                    process.wait(timeout=10)
                except psutil.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    logging.warning("Graceful shutdown failed, force killing...")
                    process.kill()
                    process.wait(timeout=5)

                logging.info("Jarvis stopped successfully")
                return True
            else:
                logging.warning("Jarvis is not running")
                return True

        except psutil.NoSuchProcess:
            logging.info("Jarvis process not found")
            return True
        except Exception as e:
            logging.error(f"Error stopping Jarvis: {e}")
            return False

    def log_restart(self):
        """Log restart information"""
        restart_info = {
            'timestamp': self.last_restart_time.isoformat() if self.last_restart_time else None,
            'restart_count': self.restart_count,
            'max_restart_attempts': self.max_restart_attempts
        }

        log_file = self.base_dir / 'logs' / 'restarts.log'
        with open(log_file, 'a') as f:
            f.write(f"{json.dumps(restart_info)}\n")

        logging.info(f"Restart #{self.restart_count} at {restart_info['timestamp']}")

    def should_restart(self):
        """Determine if Jarvis should be restarted"""
        # Check restart limit
        if self.restart_count >= self.max_restart_attempts:
            logging.warning(f"Maximum restart attempts ({self.max_restart_attempts}) reached")
            return False

        # Check if enough time has passed since last restart
        if self.last_restart_time:
            time_since_restart = datetime.now() - self.last_restart_time
            if time_since_restart < timedelta(minutes=5):
                logging.warning(f"Too soon since last restart ({time_since_restart}). Waiting...")
                return False

        return True

    def check_and_restart(self):
        """Check Jarvis status and restart if needed"""
        running, pid = self.is_jarvis_running()

        if not running:
            logging.warning("Jarvis is not running. Attempting to restart...")
            if self.should_restart():
                success, new_pid = self.start_jarvis()
                if success:
                    logging.info(f"Jarvis restarted successfully with PID: {new_pid}")
                    return True
                else:
                    logging.error("Failed to restart Jarvis")
                    return False
            else:
                logging.error("Cannot restart Jarvis - too many restart attempts")
                return False
        else:
            # Check if it's responsive
            if not self.is_jarvis_responsive():
                logging.warning("Jarvis is running but not responsive. Restarting...")
                self.stop_jarvis()
                time.sleep(5)

                if self.should_restart():
                    success, new_pid = self.start_jarvis()
                    if success:
                        logging.info(f"Jarvis restarted successfully with PID: {new_pid}")
                        return True
                    else:
                        logging.error("Failed to restart Jarvis")
                        return False
                else:
                    logging.error("Cannot restart Jarvis - too many restart attempts")
                    return False
            else:
                logging.debug("Jarvis is running and responsive")
                return True

    def run_health_check(self):
        """Run comprehensive health check"""
        try:
            health_report = self.health_monitor.generate_report()

            # Log any critical issues
            for check_name, check_result in health_report['health_check']['checks'].items():
                if check_result['status'] in ['error', 'critical']:
                    logging.warning(f"Health check failed for {check_name}: {check_result['message']}")

            return health_report['health_check']['status'] == 'healthy'

        except Exception as e:
            logging.error(f"Error running health check: {e}")
            return False

    def monitor_loop(self):
        """Main monitoring loop"""
        logging.info(f"Starting Auto Restart Monitor (check interval: {self.check_interval}s)")
        logging.info(f"Max restart attempts: {self.max_restart_attempts}, Restart delay: {self.restart_delay}s")

        # Create logs directory if it doesn't exist
        logs_dir = self.base_dir / 'logs'
        logs_dir.mkdir(exist_ok=True)

        consecutive_failures = 0

        while True:
            try:
                # Check if Jarvis is running and restart if needed
                if self.check_and_restart():
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1

                # If too many consecutive failures, stop trying
                if consecutive_failures >= 5:
                    logging.error("Too many consecutive failures. Stopping monitor.")
                    break

                # Run health check every 5 cycles
                if int(time.time()) % (self.check_interval * 5) == 0:
                    self.run_health_check()

            except KeyboardInterrupt:
                logging.info("Monitor stopped by user")
                break
            except Exception as e:
                logging.error(f"Unexpected error in monitoring loop: {e}")
                consecutive_failures += 1

            # Wait before next check
            time.sleep(self.check_interval)

    def start_daemon(self):
        """Start as a daemon process"""
        try:
            import daemon
            with daemon.DaemonContext(
                working_directory=str(self.base_dir),
                umask=0o002,
                stdout=open('logs/auto_restart.log', 'a+'),
                stderr=open('logs/auto_restart.log', 'a+')
            ):
                self.monitor_loop()
        except ImportError:
            logging.warning("python-daemon not available. Running in foreground.")
            self.monitor_loop()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Jarvis Auto Restart Monitor')
    parser.add_argument('--daemon', '-d', action='store_true', help='Run as daemon')
    parser.add_argument('--interval', '-i', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--max-restarts', '-m', type=int, default=3, help='Maximum restart attempts')
    parser.add_argument('--restart-delay', type=int, default=30, help='Delay between restarts in seconds')

    args = parser.parse_args()

    monitor = AutoRestartMonitor(
        max_restart_attempts=args.max_restarts,
        restart_delay=args.restart_delay,
        check_interval=args.interval
    )

    try:
        if args.daemon:
            monitor.start_daemon()
        else:
            monitor.monitor_loop()
    except KeyboardInterrupt:
        logging.info("Monitor stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
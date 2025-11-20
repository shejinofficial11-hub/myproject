import win32service
import win32serviceutil
import win32event
import servicemanager
import sys
import os
import subprocess
import time
from pathlib import Path

class JarvisWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "JarvisAI"
    _svc_display_name_ = "Jarvis AI Assistant"
    _svc_description_ = "Jarvis AI Assistant with Enhanced Features"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        self.base_dir = Path(__file__).parent.parent

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=10)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )

        try:
            self.main()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {e}")

    def main(self):
        # Set environment variables
        os.environ['JARVIS_ENV'] = 'production'
        os.environ['PYTHONPATH'] = str(self.base_dir)

        # Start the main application
        try:
            self.process = subprocess.Popen([
                sys.executable,
                str(self.base_dir / 'main.py')
            ],
            cwd=str(self.base_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )

            # Service loop
            while True:
                rc = win32event.WaitForSingleObject(self.hWaitStop, 1000)
                if rc == win32event.WAIT_OBJECT_0:
                    break

                # Check if process is still running
                if self.process.poll() is not None:
                    servicemanager.LogErrorMsg(f"Jarvis process exited with code: {self.process.poll()}")
                    # Restart the process
                    self.process = subprocess.Popen([
                        sys.executable,
                        str(self.base_dir / 'main.py')
                    ],
                    cwd=str(self.base_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                    )

        except Exception as e:
            servicemanager.LogErrorMsg(f"Error in main service loop: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(JarvisWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(JarvisWindowsService)
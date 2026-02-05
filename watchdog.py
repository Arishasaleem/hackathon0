# watchdog.py - Monitor and restart critical processes
import subprocess
import time
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROCESSES = {
    'orchestrator': 'python orchestrator.py',
    'gmail_watcher': 'python gmail_watcher.py',
    'file_watcher': 'python filesystem_watcher.py'
}

def is_process_running(pid_file: Path) -> bool:
    """Check if a process is running based on its PID file"""
    if not pid_file.exists():
        return False

    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())

        # Try to check if process exists (cross-platform approach)
        import psutil
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False
    except (ValueError, IOError):
        return False

def notify_human(message: str):
    """Notify human operator of important events"""
    logger.warning(f"HUMAN NOTIFICATION: {message}")
    # In a real implementation, this might send an email, SMS, etc.

def check_and_restart():
    """Check all processes and restart any that aren't running"""
    for name, cmd in PROCESSES.items():
        pid_file = Path(f'/tmp/{name}.pid')
        if not is_process_running(pid_file):
            logger.warning(f'{name} not running, restarting...')

            # Try to start the process
            try:
                # Note: This simplified version doesn't handle all the path complexities
                # In practice, you'd need to adapt the command to run from the right directory
                proc = subprocess.Popen(cmd.split())
                pid_file.write_text(str(proc.pid))
                logger.info(f'{name} restarted with PID {proc.pid}')
            except Exception as e:
                logger.error(f'Failed to restart {name}: {e}')
                notify_human(f'FAILED TO RESTART {name}: {e}')

def main():
    logger.info("Starting watchdog service...")

    while True:
        check_and_restart()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Watchdog stopped by user.")
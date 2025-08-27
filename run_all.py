import subprocess
import os
import sys

# Paths (adjust if your structure changes)
BACKEND_DIR = os.path.join(os.path.dirname(__file__), 'backend', 'src')
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend', 'src')

# Start backend
backend_proc = subprocess.Popen(
    [sys.executable, 'main.py'],
    cwd=BACKEND_DIR,
    shell=True
)
print('Backend started.')

# Start frontend
frontend_proc = subprocess.Popen(
    ['npm', 'run', 'dev'],
    cwd=FRONTEND_DIR,
    shell=True
)
print('Frontend started.')

try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print('Shutting down...')
    backend_proc.terminate()
    frontend_proc.terminate()

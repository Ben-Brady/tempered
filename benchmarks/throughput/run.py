
import os, sys
from pathlib import Path
import subprocess

def run():
    os.environ["PYTHONPATH"] = str(Path(__file__).parent.parent)
    process = subprocess.Popen([sys.executable, "throughput/servers/tempered_server.py"])
    # from servers import tempered_server

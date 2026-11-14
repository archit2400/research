import sys
from pathlib import Path

# Add project root to sys.path regardless of where script is called from
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn

if __name__ == "__main__":
    print(f"Starting ResearchPilot backend from: {ROOT_DIR}")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

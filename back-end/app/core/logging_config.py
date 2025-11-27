import logging
from pathlib import Path
from app.core.config import settings

def setup_logging():
    log_level = logging.INFO

    # Ensure the logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Log file per environment
    log_filename = "backend-dev.log" if settings.ENVIRONMENT != "local" else "backend.log"
    log_file_path = log_dir / log_filename

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )

import logging
import os
from pathlib import Path

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )

def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        "uploads",
        "processed",
        "temp",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
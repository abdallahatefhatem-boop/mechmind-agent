import logging
import os
import structlog
from datetime import datetime

# 1. Generate filename with current timestamp
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

log_dir = "logs"
root = os.getcwd()

# 2. Correct path variable name
log_path = os.path.join(root, log_dir, LOG_FILE)

# 3. Create logs directory if it doesn't exist
os.makedirs(os.path.join(root, log_dir), exist_ok=True)

# 4. Configure standard Python logging (structlog routes through this)
logging.basicConfig(
    filename=log_path,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

# Silence watchdog debug logs to prevent infinite logging loops when it watches the log directory
logging.getLogger("watchdog").setLevel(logging.WARNING)

# 5. Get logger instance
logger = structlog.get_logger()

# Example usage:
# logger.info("Application started", log_file=log_path)
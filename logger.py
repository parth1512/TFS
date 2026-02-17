import logging
import logging.handlers
import queue
import os

# Create a queue for sharing log records with the GUI
log_queue = queue.Queue()

def setup_logger():
    """
    Sets up the logger with FileHandler and QueueHandler.
    """
    logger = logging.getLogger("ModbusSlaveApp")
    logger.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File Handler
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log', maxBytes=1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Queue Handler (for GUI)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_handler.setFormatter(formatter)
    logger.addHandler(queue_handler)

    return logger

# Initialize logger instance
logger = setup_logger()

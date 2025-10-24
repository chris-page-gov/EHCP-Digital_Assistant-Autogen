"""
logging_config.py

Module for configuring the application's logging system.

This module centralises the logging configuration for the entire application.
It is designed to be called once at startup from the main entry point.

The primary function, `setup_logging`, establishes a dual-logging system:
1.  A comprehensive "root" logger that captures all output (from this application
    as well as from imported libraries like autogen, litellm, and azure) and
    directs it to both the console (stdout) and a timestamped log file.
2.  A separate, high-level "loop trace" logger (`LoopTracer`) for tracking
    only the major milestones of the application's workflow, which is useful
    for getting a quick overview of a run's progress.

"""

import os
import sys
import logging
from . import config 


def setup_logging(run_timestamp: str) -> tuple[str, str]:
    """Configures logging to capture all output to both the console and a file."""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File Handler for the full run log
    full_log_filename = f"full_run_{run_timestamp}.log"
    full_log_path = os.path.join(config.LOGS_DIR, full_log_filename)
    file_handler = logging.FileHandler(full_log_path, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Stream Handler for console output
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    
    # Separate logger for the high-level trace
    loop_log_filename = f"loop_trace_{run_timestamp}.log"
    loop_log_path = os.path.join(config.LOGS_DIR, loop_log_filename)
    loop_logger = logging.getLogger('LoopTracer')
    loop_logger.setLevel(logging.INFO)
    loop_logger.handlers.clear()
    
    loop_file_handler = logging.FileHandler(loop_log_path, mode='w', encoding='utf-8')
    loop_file_handler.setFormatter(formatter)
    loop_logger.addHandler(loop_file_handler)
    loop_logger.propagate = False
    
    logging.info(f"Logging initialised. Full log: {full_log_filename}, Loop trace: {loop_log_filename}")

    return full_log_path, loop_log_path
#!/usr/bin/env python3
"""
Document Feedback Loop Runner

This script orchestrates a feedback loop between the document writer (writer.py) and
validator (validator.py) to iteratively improve document quality.

Exit codes:
- 0: Success - validation passed
- 1: Validation failed after max iterations
- 2: Error during execution
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import time
import json

import config

# Import shared utilities
from utils import (
    setup_logging, parse_feedback_issues, ensure_directories,
    read_validation_status, has_critical_issues_in_feedback
)

# Use same Python as this script - this ensures venv is used if active
PYTHON_EXECUTABLE = sys.executable

# Setup logging
logger, log_filename = setup_logging("loop_runner")
logger.info(f"Python executable: {PYTHON_EXECUTABLE}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Virtual environment: {os.environ.get('VIRTUAL_ENV', 'Not detected')}")


class IterationTracker:
    """Track iteration history and metrics."""
    
    def __init__(self):
        self.iterations = []
        self.start_time = datetime.now()
    
    def add_iteration(self, iteration_num, writer_exit_code, validator_exit_code, 
                      has_critical_issues, issue_counts=None):
        """Add iteration results."""
        iteration_data = {
            'iteration': iteration_num,
            'timestamp': datetime.now().isoformat(),
            'writer_exit_code': writer_exit_code,
            'validator_exit_code': validator_exit_code,
            'has_critical_issues': has_critical_issues,
            'issue_counts': issue_counts or {},
            'duration_seconds': (datetime.now() - self.start_time).total_seconds()
        }
        self.iterations.append(iteration_data)
        logger.info(f"Iteration {iteration_num} tracked: {iteration_data}")
    
    def save_report(self, filepath=None):
        if filepath is None:
            filepath = config.LOOP_REPORT_PATH
        """Save iteration history to JSON file."""
        report = {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_duration_seconds': (datetime.now() - self.start_time).total_seconds(),
            'total_iterations': len(self.iterations),
            'final_status': 'PASSED' if self.iterations and not self.iterations[-1]['has_critical_issues'] else 'FAILED',
            'iterations': self.iterations
        }
        
        ensure_directories(Path(filepath).parent)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Loop report saved to {filepath}")
        return report




# Removed backup_output_folder function - working directly in output folder


def validate_python_executable(executable_path):
    """Validate that the Python executable path is safe to use."""
    import re
    
    # Convert to string and normalize path separators
    exe_str = str(Path(executable_path).resolve())
    
    # Check against valid patterns
    for pattern in config.VALID_PYTHON_PATH_PATTERNS:
        if re.search(pattern, exe_str):
            logger.info(f"Python executable validated: {exe_str}")
            return True
    
    logger.warning(f"Python executable path does not match any valid pattern: {exe_str}")
    return False


def run_subprocess(script_name, description, timeout=None):
    """
    Run a Python script as subprocess with improved error handling and security.
    
    Args:
        script_name: Name of the Python script to run
        description: Human-readable description of what's being run
        timeout: Optional timeout in seconds (defaults to config.SUBPROCESS_TIMEOUT_SECONDS)
        
    Returns:
        Exit code from the subprocess
    """
    # Validate inputs
    script_path = Path(script_name)
    if not script_path.exists():
        logger.error(f"Script not found: {script_name}")
        print(f"ERROR: Script file not found: {script_name}")
        return config.EXIT_ERROR
    
    # Validate Python executable
    if not validate_python_executable(PYTHON_EXECUTABLE):
        logger.error(f"Invalid Python executable path: {PYTHON_EXECUTABLE}")
        print(f"ERROR: Python executable path validation failed")
        return config.EXIT_ERROR
    
    # Use default timeout if not specified
    if timeout is None:
        timeout = config.SUBPROCESS_TIMEOUT_SECONDS
    
    # Log execution details
    logger.info(f"Running {description}: {script_name}")
    logger.info(f"Command: {PYTHON_EXECUTABLE} {script_name}")
    logger.info(f"Timeout: {timeout} seconds")
    
    print(f"\n{config.SEPARATOR_STANDARD}")
    print(f"Running {description}: {script_name}")
    print(f"Timeout: {timeout} seconds")
    print(f"{config.SEPARATOR_STANDARD}\n")
    
    try:
        # Run the script with timeout
        result = subprocess.run(
            [PYTHON_EXECUTABLE, script_name],
            capture_output=False,  # Let output stream to console
            text=True,
            timeout=timeout
        )
        
        logger.info(f"{description} completed with exit code: {result.returncode}")
        return result.returncode
        
    except subprocess.TimeoutExpired:
        error_msg = f"Timeout after {timeout} seconds running {script_name}"
        logger.error(error_msg)
        print(f"\nERROR: {error_msg}")
        print("The subprocess was terminated due to timeout.")
        return config.EXIT_ERROR
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Process error running {script_name}: {e}"
        logger.error(error_msg)
        print(f"\nERROR: {error_msg}")
        return e.returncode
        
    except FileNotFoundError:
        error_msg = f"Python executable not found: {PYTHON_EXECUTABLE}"
        logger.error(error_msg)
        print(f"\nERROR: {error_msg}")
        return config.EXIT_ERROR
        
    except Exception as e:
        error_msg = f"Unexpected error running {script_name}: {type(e).__name__}: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"\nERROR: {error_msg}")
        return config.EXIT_ERROR


def main():
    """Main loop runner function."""
    print("\n" + config.SEPARATOR_STANDARD)
    print("DOCUMENT FEEDBACK LOOP RUNNER")
    print(config.SEPARATOR_STANDARD)
    print(f"Max iterations: {config.MAX_ITERATIONS}")
    print(f"Python executable: {PYTHON_EXECUTABLE}")
    print(f"Virtual environment: {os.environ.get('VIRTUAL_ENV', 'Not detected')}")
    print(f"Log file: {log_filename}")
    print(config.SEPARATOR_STANDARD + "\n")
    
    logger.info("Starting document feedback loop runner")
    
    # Initialize tracker
    tracker = IterationTracker()
    
    # Check if writer.py and validator.py exist
    if not Path("writer.py").exists():
        logger.error("writer.py not found")
        print("ERROR: writer.py not found in current directory")
        return config.EXIT_ERROR
    
    if not Path("validator.py").exists():
        logger.error("validator.py not found")
        print("ERROR: validator.py not found in current directory")
        return config.EXIT_ERROR
    
    # Main loop
    for iteration in range(1, config.MAX_ITERATIONS + 1):
        print(f"\n{config.SEPARATOR_ITERATION}")
        print(f"# ITERATION {iteration} of {config.MAX_ITERATIONS}")
        print(f"{config.SEPARATOR_ITERATION}\n")
        
        logger.info(f"Starting iteration {iteration}")
        
        # Run writer.py
        writer_exit_code = run_subprocess("writer.py", "Document Writer")
        
        if writer_exit_code not in [config.EXIT_SUCCESS, config.EXIT_FIX_MODE]:  # 0=success, 2=fix mode
            logger.error(f"Writer failed with exit code {writer_exit_code}")
            print(f"\nERROR: Writer failed with exit code {writer_exit_code}")
            tracker.add_iteration(iteration, writer_exit_code, -1, True)
            break
        
        # Wait a moment for file system
        time.sleep(config.POST_WRITER_DELAY_SECONDS)
        
        # Run validator.py
        validator_exit_code = run_subprocess("validator.py", "Document Validator")
        
        # Parse feedback and validation status
        feedback_path = config.OUTPUT_DIR / config.DEFAULT_FEEDBACK_FILENAME
        status_path = config.OUTPUT_DIR / config.VALIDATION_STATUS_FILENAME
        
        # Try to read structured validation status first
        validation_status = read_validation_status(status_path, logger)
        
        if validation_status:
            # Use structured status if available
            has_critical_issues = validation_status.get('has_critical_issues', False)
            issue_counts = validation_status.get('issue_counts', {'critical': 0, 'major': 0, 'minor': 0})
            
            # Override validator exit code based on structured status
            if validation_status.get('validation_passed', False):
                validator_exit_code = config.EXIT_SUCCESS
            else:
                validator_exit_code = config.EXIT_VALIDATION_FAILED
                
            logger.info(f"Using structured validation status: {validation_status['overall_status']}")
            logger.info(f"Critical issues: {has_critical_issues}, Issue counts: {issue_counts}")
        else:
            # Fall back to old method if no structured status
            logger.warning("No validation_status.json found, falling back to feedback parsing")
            
            # Check if feedback file exists
            if not feedback_path.exists() and validator_exit_code == config.EXIT_SUCCESS:
                logger.warning("Validator returned success but no feedback file was generated")
                print("\n[WARNING] Validator completed but feedback file was not generated")
                print("This may indicate an issue with the agent calling save_feedback")
                # Treat as error since we need feedback to continue
                validator_exit_code = config.EXIT_ERROR
            
            # Parse feedback text as fallback
            if feedback_path.exists():
                has_critical_issues = has_critical_issues_in_feedback(feedback_path, logger)
                issue_counts = parse_feedback_issues(feedback_path, logger)
                
                # Override exit code based on feedback parsing
                if has_critical_issues:
                    validator_exit_code = config.EXIT_VALIDATION_FAILED
            else:
                has_critical_issues = validator_exit_code == config.EXIT_VALIDATION_FAILED
                issue_counts = None
        
        # Track iteration
        tracker.add_iteration(iteration, writer_exit_code, validator_exit_code, 
                            has_critical_issues, issue_counts)
        
        # No backup needed - working directly in output folder
        
        # Check if we should continue
        if validator_exit_code == config.EXIT_SUCCESS:
            print(f"\n{config.SEPARATOR_STANDARD}")
            print("SUCCESS: Validation passed! No critical issues found.")
            print(f"Completed in {iteration} iteration(s)")
            print(f"{config.SEPARATOR_STANDARD}\n")
            logger.info(f"Validation passed after {iteration} iterations")
            break
        elif validator_exit_code == config.EXIT_ERROR:
            logger.error(f"Validator error with exit code {validator_exit_code}")
            print(f"\nERROR: Validator failed with exit code {validator_exit_code}")
            if not feedback_path.exists():
                print("No feedback file was generated - unable to continue iteration")
            break
        else:
            # validator_exit_code == 1 (critical issues found)
            if iteration < config.MAX_ITERATIONS:
                print(f"\nValidation failed - critical issues found. Starting iteration {iteration + 1}...")
                logger.info(f"Critical issues found, continuing to iteration {iteration + 1}")
                time.sleep(config.ITERATION_DELAY_SECONDS)  # Brief pause before next iteration
            else:
                print(f"\n{config.SEPARATOR_STANDARD}")
                print(f"FAILED: Maximum iterations ({config.MAX_ITERATIONS}) reached.")
                print("Critical issues still present after all iterations.")
                print(f"{config.SEPARATOR_STANDARD}\n")
                logger.warning(f"Max iterations reached with critical issues remaining")
    
    # Save final report
    report = tracker.save_report()
    
    # Print summary
    print("\n" + config.SEPARATOR_STANDARD)
    print("LOOP RUNNER SUMMARY")
    print(config.SEPARATOR_STANDARD)
    print(f"Total iterations: {len(tracker.iterations)}")
    print(f"Final status: {report['final_status']}")
    print(f"Total duration: {report['total_duration_seconds']:.1f} seconds")
    
    if tracker.iterations:
        print("\nIteration Summary:")
        for it in tracker.iterations:
            issues = it.get('issue_counts', {})
            print(f"  Iteration {it['iteration']}: "
                  f"Critical={issues.get('critical', '?')}, "
                  f"Major={issues.get('major', '?')}, "
                  f"Minor={issues.get('minor', '?')}")
    
    print(f"\nDetailed report saved to: {config.LOOP_REPORT_PATH}")
    print(f"Log file: {log_filename}")
    print(config.SEPARATOR_STANDARD + "\n")
    
    # Return appropriate exit code
    if report['final_status'] == 'PASSED':
        return config.EXIT_SUCCESS
    else:
        return config.EXIT_VALIDATION_FAILED


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nLoop runner terminated by user.")
        logger.info("Loop runner terminated by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(2)
import logging

# Configure logging
LOG_FILE = "logs/shell.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_command(cwd: str, command: str, output: str):
    """
    Logs the current directory, shell command, and its output to shell.log.
    
    Parameters:
        cwd (str): The current working directory inside the persistent shell.
        command (str): The shell command executed.
        output (str): The output produced by the command.
    """
    logging.info(f"PWD: {cwd}")  # Log the working directory
    logging.info(f"COMMAND: {command}")  # Log the command executed
    logging.info(f"OUTPUT:\n{output}\n{'-'*50}")  # Log the output with separator

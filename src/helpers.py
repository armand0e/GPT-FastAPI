import datetime
import ast
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        log_entry = f"{datetime.datetime.now()} | {request.method} {request.url} | Status: {response.status_code}\n"
        with open("logs/api_requests.log", "a") as log_file:
            log_file.write(log_entry)
        return response
    
class FunctionReplacer(ast.NodeTransformer):
    def __init__(self, target_name: str, new_node: ast.FunctionDef):
        self.target_name = target_name
        self.new_node = new_node
        self.replaced = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.target_name:
            self.replaced = True
            return self.new_node
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if node.name == self.target_name:
            self.replaced = True
            return self.new_node
        return self.generic_visit(node)
    
class ProcessManager:
    """Manages running processes with unique numeric IDs."""
    def __init__(self):
        self.processes = {}  # Stores {process_id: {name, command, process}}
        self.next_process_id = 1  # Starts from 1

    def add_process(self, name: str, command: str, process):
        """Adds a new process and assigns it a unique ID."""
        process_id = self.next_process_id
        self.processes[process_id] = {"name": name, "command": command, "process": process}
        self.next_process_id += 1
        return process_id

    def get_process(self, process_id: int):
        """Retrieves a process by its ID."""
        return self.processes.get(process_id, None)

    def remove_process(self, process_id: int):
        """Removes a process by its ID."""
        if process_id in self.processes:
            del self.processes[process_id]

class Shell:
    """Represents a persistent shell session."""
    def __init__(self, shell_id: int, name: str, process):
        self.shell_id = shell_id
        self.name = name
        self.process = process

class ShellManager:
    """Manages multiple persistent shells."""
    def __init__(self):
        self.shells = {}  # Stores {shell_id: Shell object}
        self.next_shell_id = 1  # Starts from 1

    def add_shell(self, name: str, process):
        """Adds a new shell and assigns it a unique ID."""
        shell_id = self.next_shell_id
        self.shells[shell_id] = Shell(shell_id, name, process)
        self.next_shell_id += 1
        return shell_id

    def get_shell(self, shell_id: int):
        """Retrieves a shell by its ID."""
        return self.shells.get(shell_id, None)

    def remove_shell(self, shell_id: int):
        """Removes a shell by its ID."""
        if shell_id in self.shells:
            del self.shells[shell_id]

shell_manager = ShellManager()  # Global instance

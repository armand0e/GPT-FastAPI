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

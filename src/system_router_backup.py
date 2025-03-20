import asyncio
import os
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from logger import system_logger
logger = system_logger
router = APIRouter()
running_processes = {}

class CDRequest(BaseModel):
    directory: str

class CommandRequest(BaseModel):
    command: str

@router.post('/set-current-directory')
async def change_current_directory(request: CDRequest):
    """Changes the current working directory."""
    if not os.path.exists(request.directory):
        raise HTTPException(status_code=400, detail='Invalid directory path')
    os.chdir(request.directory)
    logger.info(f'Current directory changed to {request.directory}')
    return {'message': f'Current directory changed to {request.directory}'}

@router.post('/get-current-directory')
async def return_current_directory():
    """Returns the current working directory."""
    return {'message': f'The current working directory is {os.getcwd()}'}

@router.post('/run-command')
async def run_terminal_command(request: CommandRequest):
    """Runs a terminal command and returns its output."""
    try:
        process = await asyncio.create_subprocess_shell(request.command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        (stdout, stderr) = await process.communicate()
        output = stdout.decode().strip()
        error = stderr.decode().strip()
        logger.info(f'Executed command: {request.command} | Output: {output} | Error: {error}')
        return {'input': request.command, 'output': output, 'error': error}
    except Exception as e:
        logger.error(f'Command execution failed: {request.command} | Error: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Command execution error: {str(e)}')

async def run_long_command_to_log(command: str, process_id: str):
    """
    Runs a long-running command asynchronously.
    Writes the command, its output, and errors continuously to a log file in tmp/{process_id}.log.
    """
    os.makedirs('tmp', exist_ok=True)
    log_file_path = f'tmp/{process_id}.log'
    with open(log_file_path, 'w') as log_file:
        log_file.write(f'Command: {command}\n')
        log_file.flush()
        process = await asyncio.create_subprocess_shell(command, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        running_processes[process_id] = {'process': process, 'log_file': log_file_path, 'stdin': process.stdin}
        while True:
            line = await process.stdout.readline()
            if not line:
                if process.returncode is not None:
                    break
                await asyncio.sleep(0.1)
                continue
            log_file.write(line.decode())
            log_file.flush()
        await process.wait()

def cleanup_processes():
    """Terminates all running subprocesses on exit."""
    for (process_id, proc_info) in running_processes.items():
        process = proc_info.get('process')
        if process and process.returncode is None:
            try:
                process.terminate()
            except Exception as e:
                logger.error(f'Error terminating process {process_id}: {e}')
    logger.info('All running subprocesses have been cleaned up.')

@router.post('/start-process')
async def start_process(request: CommandRequest):
    """
    Starts a long-running process in the background.
    Returns immediately with a success message and a unique process ID.
    """
    process_id = str(uuid.uuid4())
    asyncio.create_task(run_long_command_to_log(request.command, process_id))
    return {'message': 'Process started', 'process_id': process_id}

@router.post('/stop-process/{process_id}')
async def stop_process(process_id: str):
    """
    Stops a running process given its process ID and deletes its log file.
    """
    if process_id not in running_processes:
        raise HTTPException(status_code=404, detail='Process not found')
    proc_info = running_processes[process_id]
    process = proc_info.get('process')
    log_file_path = proc_info.get('log_file')
    if process and process.returncode is None:
        process.terminate()
        await process.wait()
    if log_file_path and os.path.exists(log_file_path):
        try:
            os.remove(log_file_path)
        except Exception as e:
            logger.error(f'Failed to remove log file for process {process_id}: {e}')
            raise HTTPException(status_code=500, detail=f'Failed to delete log file: {e}')
    del running_processes[process_id]
    return {'message': 'Process terminated and log file deleted'}

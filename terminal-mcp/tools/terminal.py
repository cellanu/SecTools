"""
Terminal MCP Server - Terminal Tool Implementation

This module provides the execute_command tool for running terminal commands
with async subprocess execution, timeout control, and comprehensive error handling.
"""

import asyncio
import os
import sys
import time
from typing import Optional
from dataclasses import dataclass

# Import security filter
from security.filter import get_filter, CommandFilter


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float


def get_default_shell() -> list[str]:
    """
    Get the default shell for the current operating system.
    
    Returns:
        List of shell command and arguments.
    """
    if sys.platform == 'win32':
        # Windows: prefer PowerShell, fallback to CMD
        return ['powershell', '-Command']
    elif sys.platform == 'darwin':
        # macOS: use bash or zsh
        shell = os.environ.get('SHELL', '/bin/bash')
        return [shell, '-c']
    else:
        # Linux and others: use bash or sh
        return ['/bin/sh', '-c']


async def execute_command(
    command: str,
    working_directory: Optional[str] = None,
    timeout: Optional[int] = None,
    filter_instance: Optional[CommandFilter] = None
) -> CommandResult:
    """
    Execute a terminal command asynchronously.
    
    Args:
        command: The command to execute.
        working_directory: Directory to execute the command in.
                          Defaults to current working directory.
        timeout: Maximum execution time in seconds.
                Defaults to configured default timeout.
        filter_instance: Security filter instance.
                        Defaults to global filter.
    
    Returns:
        CommandResult with execution details.
    """
    start_time = time.time()
    
    # Get security filter
    if filter_instance is None:
        filter_instance = get_filter()
    
    # Get timeout configuration
    if timeout is None:
        timeout = filter_instance.get_default_timeout()
    
    # Enforce maximum timeout
    max_timeout = filter_instance.get_max_timeout()
    if timeout > max_timeout:
        return CommandResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=f"Requested timeout ({timeout}s) exceeds maximum allowed ({max_timeout}s)",
            execution_time=0.0
        )
    
    # Validate command through security filter
    validation = filter_instance.validate_command(command, working_directory)
    if not validation.is_valid:
        return CommandResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=f"Command blocked by security filter: {validation.reason}",
            execution_time=0.0
        )
    
    # Determine working directory
    if working_directory:
        if not os.path.isdir(working_directory):
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Working directory does not exist: {working_directory}",
                execution_time=0.0
            )
        cwd = working_directory
    else:
        cwd = os.getcwd()
    
    # Prepare shell command
    shell_cmd = get_default_shell()
    
    try:
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *shell_cmd,
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        
        try:
            # Wait for completion with timeout
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            # Decode output with error handling
            stdout = _decode_output(stdout_bytes)
            stderr = _decode_output(stderr_bytes)
            
            exit_code = process.returncode or 0
            success = (exit_code == 0)
            
        except asyncio.TimeoutError:
            # Kill the process on timeout
            try:
                process.kill()
                await process.wait()
            except ProcessLookupError:
                pass
            
            execution_time = time.time() - start_time
            
            # Try to get any partial output
            partial_stdout = ""
            try:
                if process.stdout:
                    process.stdout._buffer.clear()
            except Exception:
                pass
            
            return CommandResult(
                success=False,
                exit_code=-2,  # Special code for timeout
                stdout=partial_stdout,
                stderr=f"Command timed out after {timeout} seconds",
                execution_time=execution_time
            )
            
    except FileNotFoundError as e:
        # Command not found
        execution_time = time.time() - start_time
        return CommandResult(
            success=False,
            exit_code=127,
            stdout="",
            stderr=f"Command not found: {command}\nDetails: {str(e)}",
            execution_time=execution_time
        )
    except PermissionError as e:
        # Permission denied
        execution_time = time.time() - start_time
        return CommandResult(
            success=False,
            exit_code=126,
            stdout="",
            stderr=f"Permission denied: {command}\nDetails: {str(e)}",
            execution_time=execution_time
        )
    except OSError as e:
        # Other OS errors
        execution_time = time.time() - start_time
        return CommandResult(
            success=False,
            exit_code=-3,
            stdout="",
            stderr=f"OS error executing command: {str(e)}",
            execution_time=execution_time
        )
    except Exception as e:
        # Unexpected errors
        execution_time = time.time() - start_time
        return CommandResult(
            success=False,
            exit_code=-99,
            stdout="",
            stderr=f"Unexpected error: {type(e).__name__}: {str(e)}",
            execution_time=execution_time
        )
    
    execution_time = time.time() - start_time
    
    # Log execution
    filter_instance.log_execution(
        command=command,
        working_directory=working_directory,
        timeout=timeout,
        success=success,
        exit_code=exit_code,
        execution_time=execution_time,
        stdout=stdout,
        stderr=stderr
    )
    
    return CommandResult(
        success=success,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        execution_time=execution_time
    )


def _decode_output(data: bytes) -> str:
    """
    Decode binary output with multiple encoding fallbacks.
    
    Args:
        data: Binary data to decode.
        
    Returns:
        Decoded string.
    """
    if not data:
        return ""
    
    # Try common encodings in order
    encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            return data.decode(encoding, errors='replace')
        except (UnicodeDecodeError, LookupError):
            continue
    
    # Final fallback: decode with replacement
    return data.decode('utf-8', errors='replace')


async def safe_read_stream(stream) -> str:
    """
    Safely read from an async stream.
    
    Args:
        stream: Async subprocess stream.
        
    Returns:
        Stream content as string.
    """
    if stream is None:
        return ""
    try:
        data = await stream.read()
        return _decode_output(data)
    except Exception:
        return ""


async def execute_command_with_progress(
    command: str,
    working_directory: Optional[str] = None,
    timeout: Optional[int] = None,
    filter_instance: Optional[CommandFilter] = None,
    output_callback=None
) -> CommandResult:
    """
    Execute a command with real-time output callback.
    
    This version streams output as it becomes available, useful for
    long-running commands where you want to see progress.
    
    Args:
        command: The command to execute.
        working_directory: Directory to execute the command in.
        timeout: Maximum execution time in seconds.
        filter_instance: Security filter instance.
        output_callback: Async callback function for output chunks.
                        Called as: await callback(chunk, is_stderr)
    
    Returns:
        CommandResult with execution details.
    """
    start_time = time.time()
    
    # Get security filter
    if filter_instance is None:
        filter_instance = get_filter()
    
    # Get timeout configuration
    if timeout is None:
        timeout = filter_instance.get_default_timeout()
    
    # Enforce maximum timeout
    max_timeout = filter_instance.get_max_timeout()
    if timeout > max_timeout:
        return CommandResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=f"Requested timeout ({timeout}s) exceeds maximum allowed ({max_timeout}s)",
            execution_time=0.0
        )
    
    # Validate command through security filter
    validation = filter_instance.validate_command(command, working_directory)
    if not validation.is_valid:
        return CommandResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=f"Command blocked by security filter: {validation.reason}",
            execution_time=0.0
        )
    
    # Determine working directory
    if working_directory:
        if not os.path.isdir(working_directory):
            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Working directory does not exist: {working_directory}",
                execution_time=0.0
            )
        cwd = working_directory
    else:
        cwd = os.getcwd()
    
    # Prepare shell command
    shell_cmd = get_default_shell()
    
    stdout_chunks = []
    stderr_chunks = []
    
    try:
        # Create subprocess with line-buffered output
        process = await asyncio.create_subprocess_exec(
            *shell_cmd,
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        
        async def read_stream(stream, is_stderr):
            """Read from stream and collect/output chunks."""
            chunks = []
            while True:
                try:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded = _decode_output(line)
                    chunks.append(decoded)
                    
                    if output_callback:
                        try:
                            await output_callback(decoded, is_stderr)
                        except Exception:
                            pass  # Don't let callback errors stop execution
                except asyncio.IncompleteReadError as e:
                    if e.partial:
                        decoded = _decode_output(e.partial)
                        chunks.append(decoded)
                        if output_callback:
                            try:
                                await output_callback(decoded, is_stderr)
                            except Exception:
                                pass
                    break
                except Exception:
                    break
            return ''.join(chunks)
        
        try:
            # Run both readers concurrently with timeout
            stdout_result, stderr_result = await asyncio.wait_for(
                asyncio.gather(
                    read_stream(process.stdout, False),
                    read_stream(process.stderr, True),
                ),
                timeout=timeout
            )
            
            stdout = stdout_result
            stderr = stderr_result
            
            # Wait for process to complete
            await process.wait()
            exit_code = process.returncode or 0
            success = (exit_code == 0)
            
        except asyncio.TimeoutError:
            # Kill the process on timeout
            try:
                process.kill()
                await process.wait()
            except ProcessLookupError:
                pass
            
            execution_time = time.time() - start_time
            
            return CommandResult(
                success=False,
                exit_code=-2,
                stdout=''.join(stdout_chunks),
                stderr=f"Command timed out after {timeout} seconds\n" + ''.join(stderr_chunks),
                execution_time=execution_time
            )
            
    except FileNotFoundError as e:
        execution_time = time.time() - start_time
        return CommandResult(
            success=False,
            exit_code=127,
            stdout="",
            stderr=f"Command not found: {command}\nDetails: {str(e)}",
            execution_time=execution_time
        )
    except PermissionError as e:
        execution_time = time.time() - start_time
        return CommandResult(
            success=False,
            exit_code=126,
            stdout="",
            stderr=f"Permission denied: {command}\nDetails: {str(e)}",
            execution_time=execution_time
        )
    except Exception as e:
        execution_time = time.time() - start_time
        return CommandResult(
            success=False,
            exit_code=-99,
            stdout="",
            stderr=f"Unexpected error: {type(e).__name__}: {str(e)}",
            execution_time=execution_time
        )
    
    execution_time = time.time() - start_time
    
    # Log execution
    filter_instance.log_execution(
        command=command,
        working_directory=working_directory,
        timeout=timeout,
        success=success,
        exit_code=exit_code,
        execution_time=execution_time,
        stdout=stdout,
        stderr=stderr
    )
    
    return CommandResult(
        success=success,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        execution_time=execution_time
    )

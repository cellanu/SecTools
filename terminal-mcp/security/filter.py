"""
Terminal MCP Server - Security Filter Module

This module provides security filtering for terminal commands, including:
- Command whitelist/blacklist validation
- Dangerous pattern detection
- Working directory validation
- Audit logging
"""

import re
import os
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class SecurityConfig:
    """Security configuration data class."""
    enable_command_filter: bool = True
    allow_commands: list[str] = field(default_factory=list)
    deny_commands: list[str] = field(default_factory=list)
    max_timeout: int = 300
    default_timeout: int = 30
    dangerous_patterns: list[str] = field(default_factory=list)
    allowed_directories: list[str] = field(default_factory=list)
    forbidden_directories: list[str] = field(default_factory=list)
    
    # Logging config
    log_level: str = "INFO"
    log_file: str = "logs/audit.log"
    max_log_size_mb: int = 100
    backup_count: int = 5
    include_output: bool = True
    preview_length: int = 500


@dataclass
class ValidationResult:
    """Result of command validation."""
    is_valid: bool
    reason: str = ""
    blocked_by: str = ""  # whitelist, blacklist, pattern, directory


class CommandFilter:
    """
    Security filter for terminal commands.
    
    Validates commands against configured security policies including
    whitelists, blacklists, and dangerous pattern detection.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the command filter.
        
        Args:
            config_path: Path to the YAML configuration file.
                        If None, uses default configuration.
        """
        self.config = SecurityConfig()
        self.dangerous_regexes: list[re.Pattern] = []
        self.logger: Optional[logging.Logger] = None
        
        if config_path:
            self.load_config(config_path)
        else:
            # Try to load from default location
            default_paths = [
                "config/config.yaml",
                os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml"),
            ]
            for path in default_paths:
                if os.path.exists(path):
                    self.load_config(path)
                    break
        
        self._compile_dangerous_patterns()
        self._setup_logging()
    
    def load_config(self, config_path: str) -> None:
        """
        Load security configuration from YAML file.
        
        Args:
            config_path: Path to the YAML configuration file.
            
        Raises:
            FileNotFoundError: If config file doesn't exist.
            yaml.YAMLError: If config file is invalid YAML.
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return
            
        security = data.get('security', {})
        logging_config = data.get('logging', {})
        
        self.config = SecurityConfig(
            enable_command_filter=security.get('enable_command_filter', True),
            allow_commands=security.get('allow_commands', []),
            deny_commands=security.get('deny_commands', []),
            max_timeout=security.get('max_timeout', 300),
            default_timeout=security.get('default_timeout', 30),
            dangerous_patterns=security.get('dangerous_patterns', []),
            allowed_directories=security.get('allowed_directories', []),
            forbidden_directories=security.get('forbidden_directories', []),
            log_level=logging_config.get('level', 'INFO'),
            log_file=logging_config.get('file', 'logs/audit.log'),
            max_log_size_mb=logging_config.get('max_size_mb', 100),
            backup_count=logging_config.get('backup_count', 5),
            include_output=logging_config.get('include_output', True),
            preview_length=logging_config.get('preview_length', 500),
        )
    
    def _compile_dangerous_patterns(self) -> None:
        """Compile dangerous patterns into regex objects."""
        self.dangerous_regexes = []
        for pattern in self.config.dangerous_patterns:
            try:
                self.dangerous_regexes.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                if self.logger:
                    self.logger.warning(f"Invalid regex pattern '{pattern}': {e}")
    
    def _setup_logging(self) -> None:
        """Setup audit logging."""
        self.logger = logging.getLogger('terminal_mcp_security')
        self.logger.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))
        
        # Ensure log directory exists
        log_dir = os.path.dirname(self.config.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # File handler with rotation
        if self.config.log_file:
            try:
                from logging.handlers import RotatingFileHandler
                handler = RotatingFileHandler(
                    self.config.log_file,
                    maxBytes=self.config.max_log_size_mb * 1024 * 1024,
                    backupCount=self.config.backup_count
                )
                formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            except Exception as e:
                self.logger.warning(f"Failed to setup file logging: {e}")
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        self.logger.addHandler(console_handler)
    
    def validate_command(self, command: str, working_directory: Optional[str] = None) -> ValidationResult:
        """
        Validate a command against security policies.
        
        Args:
            command: The command to validate.
            working_directory: The working directory for the command.
            
        Returns:
            ValidationResult indicating whether the command is allowed.
        """
        if not self.config.enable_command_filter:
            return ValidationResult(is_valid=True)
        
        # Extract the base command (first word)
        base_command = self._extract_base_command(command)
        
        # Check blacklist first (always applied)
        if self._is_blacklisted(base_command):
            return ValidationResult(
                is_valid=False,
                reason=f"Command '{base_command}' is in the deny list",
                blocked_by="blacklist"
            )
        
        # Check dangerous patterns
        pattern_match = self._check_dangerous_patterns(command)
        if pattern_match:
            return ValidationResult(
                is_valid=False,
                reason=f"Command matches dangerous pattern: {pattern_match}",
                blocked_by="pattern"
            )
        
        # Check whitelist (if configured)
        if self.config.allow_commands:
            if not self._is_whitelisted(base_command):
                return ValidationResult(
                    is_valid=False,
                    reason=f"Command '{base_command}' is not in the allow list",
                    blocked_by="whitelist"
                )
        
        # Check working directory restrictions
        if working_directory:
            dir_result = self._validate_directory(working_directory)
            if not dir_result.is_valid:
                return dir_result
        
        return ValidationResult(is_valid=True)
    
    def _extract_base_command(self, command: str) -> str:
        """
        Extract the base command from a command string.
        
        Handles pipes, redirects, and complex shell syntax.
        
        Args:
            command: The full command string.
            
        Returns:
            The base command name.
        """
        # Remove leading/trailing whitespace
        command = command.strip()
        
        # Handle empty command
        if not command:
            return ""
        
        # Split on common shell operators and take the first part
        # This handles cases like: cmd1 | cmd2, cmd1 && cmd2, cmd1 > file
        for separator in ['|', '&&', '||', ';', '>', '>>', '&']:
            if separator in command:
                command = command.split(separator)[0].strip()
        
        # Get the first word (the actual command)
        parts = command.split()
        if not parts:
            return ""
        
        base = parts[0]
        
        # Remove path prefix if present
        if '/' in base or '\\' in base:
            base = os.path.basename(base)
        
        return base.lower()
    
    def _is_blacklisted(self, command: str) -> bool:
        """Check if command is in the blacklist."""
        if not command:
            return False
        return command.lower() in [c.lower() for c in self.config.deny_commands]
    
    def _is_whitelisted(self, command: str) -> bool:
        """Check if command is in the whitelist."""
        if not command:
            return False
        return command.lower() in [c.lower() for c in self.config.allow_commands]
    
    def _check_dangerous_patterns(self, command: str) -> Optional[str]:
        """
        Check if command matches any dangerous patterns.
        
        Returns:
            The matched pattern description, or None if no match.
        """
        for i, regex in enumerate(self.dangerous_regexes):
            if regex.search(command):
                return self.config.dangerous_patterns[i]
        return None
    
    def _validate_directory(self, directory: str) -> ValidationResult:
        """
        Validate the working directory.
        
        Args:
            directory: The directory path to validate.
            
        Returns:
            ValidationResult indicating whether the directory is allowed.
        """
        # Normalize the path
        try:
            abs_path = os.path.abspath(directory)
        except Exception:
            return ValidationResult(
                is_valid=False,
                reason=f"Invalid directory path: {directory}",
                blocked_by="directory"
            )
        
        # Check forbidden directories
        for forbidden in self.config.forbidden_directories:
            if abs_path.startswith(forbidden):
                return ValidationResult(
                    is_valid=False,
                    reason=f"Directory '{directory}' is within forbidden path '{forbidden}'",
                    blocked_by="directory"
                )
        
        # Check allowed directories (if configured)
        if self.config.allowed_directories:
            is_allowed = False
            for allowed in self.config.allowed_directories:
                if abs_path.startswith(allowed):
                    is_allowed = True
                    break
            if not is_allowed:
                return ValidationResult(
                    is_valid=False,
                    reason=f"Directory '{directory}' is not in the allowed list",
                    blocked_by="directory"
                )
        
        return ValidationResult(is_valid=True)
    
    def log_execution(
        self,
        command: str,
        working_directory: Optional[str],
        timeout: int,
        success: bool,
        exit_code: int,
        execution_time: float,
        stdout: str = "",
        stderr: str = ""
    ) -> None:
        """
        Log command execution for audit purposes.
        
        Args:
            command: The executed command.
            working_directory: The working directory used.
            timeout: The timeout value.
            success: Whether execution was successful.
            exit_code: The command exit code.
            execution_time: Execution time in seconds.
            stdout: Standard output (truncated).
            stderr: Standard error (truncated).
        """
        if not self.logger:
            return
        
        # Truncate output if configured
        if self.config.include_output:
            stdout_preview = stdout[:self.config.preview_length]
            stderr_preview = stderr[:self.config.preview_length]
            if len(stdout) > self.config.preview_length:
                stdout_preview += "... (truncated)"
            if len(stderr) > self.config.preview_length:
                stderr_preview += "... (truncated)"
        else:
            stdout_preview = "<output hidden>"
            stderr_preview = "<output hidden>"
        
        status = "SUCCESS" if success else "FAILED"
        
        log_entry = (
            f"AUDIT | CMD: {command} | DIR: {working_directory or '.'} | "
            f"TIMEOUT: {timeout}s | STATUS: {status} | EXIT: {exit_code} | "
            f"DURATION: {execution_time:.3f}s | STDOUT: {stdout_preview} | STDERR: {stderr_preview}"
        )
        
        if success:
            self.logger.info(log_entry)
        else:
            self.logger.warning(log_entry)
    
    def get_max_timeout(self) -> int:
        """Get the maximum allowed timeout from configuration."""
        return self.config.max_timeout
    
    def get_default_timeout(self) -> int:
        """Get the default timeout from configuration."""
        return self.config.default_timeout


# Singleton instance for convenience
_filter_instance: Optional[CommandFilter] = None


def get_filter(config_path: Optional[str] = None) -> CommandFilter:
    """
    Get or create the global CommandFilter instance.
    
    Args:
        config_path: Optional path to configuration file.
        
    Returns:
        CommandFilter instance.
    """
    global _filter_instance
    if _filter_instance is None:
        _filter_instance = CommandFilter(config_path)
    return _filter_instance

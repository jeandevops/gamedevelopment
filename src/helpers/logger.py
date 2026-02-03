import logging
import sys
from typing import Optional

class GameLogger:
    """
    Centralized logging system for the game.
    Provides structured logging with different severity levels.
    """
    
    _instance: Optional['GameLogger'] = None
    
    def __new__(cls):
        """Singleton pattern - ensures only one logger instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the logger (only once due to singleton pattern)"""
        if self._initialized:
            return
        
        self._initialized = True
        
        # Create logger
        self.logger = logging.getLogger("GameEngine")
        self.logger.setLevel(logging.DEBUG)
        
        # Create console handler with detailed formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            fmt='[%(levelname)-8s] %(asctime)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message"""
        self.logger.critical(message)


# Singleton instance for easy import
logger = GameLogger()

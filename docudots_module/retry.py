"""
Retry and timeout utilities for DocuDots PDF Analysis Module
============================================================
"""

import time
import signal
import functools
import logging
from typing import Callable, Any, Type, Tuple, Optional

from exceptions import AnalysisTimeoutError, CircuitBreakerOpenError


def with_retry(max_attempts: int = 3, 
               delay: float = 1.0, 
               backoff: float = 2.0,
               exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Exponential backoff multiplier
        exceptions: Tuple of exceptions to retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(func.__module__)
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    if attempt > 0:  # Log successful retry
                        logger.info(f"Retry: {func.__name__} succeeded on attempt {attempt + 1}")
                    
                    logger.info(f"Performance: {func.__name__} completed in {elapsed:.2f}s")
                    return result
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt failed
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                        break
                    
                    # Calculate wait time with exponential backoff
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                                 f"Retrying in {wait_time:.1f}s...")
                    
                    time.sleep(wait_time)
            
            # All attempts failed, raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


def with_timeout(timeout_seconds: int):
    """
    Timeout decorator using signal alarm.
    
    Args:
        timeout_seconds: Timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(func.__module__)
            
            def timeout_handler(signum, frame):
                raise AnalysisTimeoutError(f"Function {func.__name__} timed out after {timeout_seconds}s")
            
            # Set up timeout (Unix-like systems only)
            old_handler = None
            try:
                if hasattr(signal, 'SIGALRM'):
                    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(timeout_seconds)
                
                result = func(*args, **kwargs)
                return result
            
            except AnalysisTimeoutError:
                logger.error(f"Timeout: {func.__name__} exceeded {timeout_seconds}s limit")
                raise
            
            finally:
                # Clean up timeout
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                    if old_handler:
                        signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by temporarily disabling operations
    that are likely to fail based on recent failure history.
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(__name__)
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                    self.logger.info(f"Circuit breaker HALF_OPEN for {func.__name__}")
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN for {func.__name__}. "
                        f"Try again after {self.timeout}s"
                    )
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            
            except Exception as e:
                self._on_failure()
                raise
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.timeout
    
    def _on_success(self) -> None:
        """Handle successful operation."""
        if self.state == 'HALF_OPEN':
            self.logger.info("Circuit breaker reset to CLOSED")
            self.state = 'CLOSED'
        self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            self.logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")


# Default circuit breaker instance
default_circuit_breaker = CircuitBreaker()

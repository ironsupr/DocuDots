#!/usr/bin/env python3
"""
Retry utilities for DocuDots PDF Structure Analysis Tool
Adobe India Hackathon - Challenge 1A
"""

import time
import functools
import logging
from typing import Callable, Any, Type, Tuple, Optional

from .exceptions import PDFProcessingError, ResourceLimitError

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 1.5,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    exclude_exceptions: Tuple[Type[Exception], ...] = (),
    on_retry: Optional[Callable] = None
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        exceptions: Tuple of exceptions to retry on
        exclude_exceptions: Tuple of exceptions to never retry
        on_retry: Optional callback function called on each retry
    
    Example:
        @retry(max_attempts=3, backoff_factor=2.0)
        def process_pdf(pdf_path):
            # Your processing code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                
                except exclude_exceptions as e:
                    # Don't retry these exceptions
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt failed
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                        break
                    
                    # Calculate wait time with exponential backoff
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                                 f"Retrying in {wait_time:.1f}s...")
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e, wait_time)
                        except Exception as callback_error:
                            logger.warning(f"Retry callback failed: {callback_error}")
                    
                    time.sleep(wait_time)
            
            # All attempts failed, raise the last exception
            if last_exception:
                if isinstance(last_exception, PDFProcessingError):
                    raise last_exception
                else:
                    raise PDFProcessingError(
                        f"Failed after {max_attempts} attempts: {last_exception}",
                        stage="retry_exhausted"
                    ) from last_exception
            
        return wrapper
    return decorator


def timeout(seconds: int = 300):
    """
    Timeout decorator for long-running operations.
    
    Args:
        seconds: Timeout in seconds (default: 5 minutes)
    
    Example:
        @timeout(seconds=60)
        def process_large_pdf(pdf_path):
            # Processing code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import signal
            
            class TimeoutError(Exception):
                pass
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            # Set up the timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
                return result
            except TimeoutError as e:
                logger.error(f"Timeout in {func.__name__}: {e}")
                raise ResourceLimitError(
                    f"Processing timed out after {seconds} seconds",
                    resource_type="processing_time",
                    limit=f"{seconds}s"
                ) from e
            finally:
                # Clean up the alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator


def log_performance(func: Callable) -> Callable:
    """
    Decorator to log function performance metrics.
    
    Args:
        func: Function to monitor
    
    Example:
        @log_performance
        def extract_text_blocks(pdf):
            # Processing code here
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.info(f"Performance: {func.__name__} completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.error(f"Performance: {func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    
    return wrapper


class CircuitBreaker:
    """
    Circuit breaker pattern for handling repeated failures.
    
    This prevents cascading failures by temporarily stopping
    attempts to perform operations that are likely to fail.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                    logger.info(f"Circuit breaker for {func.__name__} moving to HALF_OPEN")
                else:
                    raise PDFProcessingError(
                        f"Circuit breaker is OPEN for {func.__name__}. "
                        f"Too many recent failures ({self.failure_count}/{self.failure_threshold})",
                        stage="circuit_breaker"
                    )
            
            try:
                result = func(*args, **kwargs)
                
                # Success - reset circuit breaker
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                    logger.info(f"Circuit breaker for {func.__name__} reset to CLOSED")
                
                return result
                
            except Exception as e:
                self._record_failure()
                logger.warning(f"Circuit breaker recorded failure for {func.__name__}: {e}")
                raise
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _record_failure(self):
        """Record a failure and update circuit breaker state."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker opened due to {self.failure_count} failures")


# Pre-configured retry decorators for common scenarios
retry_pdf_operations = retry(
    max_attempts=3,
    backoff_factor=1.5,
    exceptions=(PDFProcessingError, IOError, OSError),
    exclude_exceptions=(ResourceLimitError, KeyboardInterrupt)
)

retry_file_operations = retry(
    max_attempts=2,
    backoff_factor=1.0,
    exceptions=(IOError, OSError, PermissionError),
    exclude_exceptions=(FileNotFoundError,)
)

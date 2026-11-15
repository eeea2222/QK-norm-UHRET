"""Compatibility import. Scientific evaluation is deferred; eval now runs software tests only."""
from .software_eval import run_eval
__all__ = ['run_eval']

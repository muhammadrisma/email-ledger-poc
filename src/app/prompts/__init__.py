"""
Prompt templates for AI extraction and classification.
"""

from .financial_extraction import FINANCIAL_EXTRACTION_PROMPT
from .expense_classification import EXPENSE_CLASSIFICATION_PROMPT

__all__ = [
    'FINANCIAL_EXTRACTION_PROMPT',
    'EXPENSE_CLASSIFICATION_PROMPT'
] 
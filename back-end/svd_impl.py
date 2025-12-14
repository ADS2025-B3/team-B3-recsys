"""
Wrapper module to make svd_impl importable by MLflow models.
This allows models saved with 'import svd_impl' to be loaded in the backend.
"""
from app.models.svd_impl import SVDCF

__all__ = ['SVDCF']

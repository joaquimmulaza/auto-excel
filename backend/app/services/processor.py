"""Services layer entry point for table processing."""

from backend.app.domain.engine import TableProcessor, process_price_table

__all__ = ["TableProcessor", "process_price_table"]

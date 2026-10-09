"""Single place that configures logging. Call `configure_logging()` once from an entrypoint.

The original server called logging.basicConfig in nearly every module; only the first
call wins and the rest are silent no-ops. Centralizing avoids that confusion.
"""
import logging

_configured = False


def configure_logging(level: str = "INFO") -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    _configured = True

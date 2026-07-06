import logging
import sys

def setup_logging():
    """
    Configure clean stdout logging for SentinelOps.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger("sentinelsops")
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logging()

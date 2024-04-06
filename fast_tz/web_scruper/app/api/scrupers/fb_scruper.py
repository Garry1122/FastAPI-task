
import logging
import time

logger = logging.getLogger(__name__)


def fb_scruper(args):
    logger.info("Starting Scrupping from fb")
    time.sleep(30)
    logger.info("Scrupping from fb finished")
    return {"message": "ok"}

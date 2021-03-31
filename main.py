import logging

from rich.logging import RichHandler
from rich.traceback import install

from db import connection

install()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)
if __name__ == "__main__":
    conn = connection()
    cur = conn.cursor()
    logger = logging.getLogger("main")
    logger.info([conn, cur])
    logger.info("Ready")

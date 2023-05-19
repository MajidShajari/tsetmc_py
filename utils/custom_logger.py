import logging
import logging.handlers
import datetime
import pathlib
from queue import Queue


def configure_logging(log_file_path: str = "", level: str = "debug"):
    log_level = getattr(logging, level.upper(), logging.DEBUG)

    logging.getLogger().setLevel(log_level)

    # Create the formatter
    formatter = logging.Formatter(
        '%(asctime)-20s - %(funcName)-25s -> %(levelname)-10s : %(message)s')

    # Create the console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

    # Create the file handler
    if log_file_path:
        pathlib.Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    # Create the queue handler
    queue = Queue(-1)
    queue_handler = logging.handlers.QueueHandler(queue)
    logging.getLogger().addHandler(queue_handler)

    # Create the queue listener
    queue_listener = logging.handlers.QueueListener(
        queue, file_handler if log_file_path else console_handler)  # type: ignore
    queue_listener.start()


if __name__ == "__main__":
    pathlib.Path.cwd().joinpath("log").mkdir(parents=True, exist_ok=True)
    LOG_PATH = "log/test.log"
    configure_logging(log_file_path=LOG_PATH)
    logger = logging.getLogger(__name__)
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
    logger.critical('Critical message')
else:
    pathlib.Path.cwd().joinpath("log").mkdir(parents=True, exist_ok=True)
    LOG_PATH = f"log/{datetime.date.today()}-tsetmc.log"
    configure_logging(log_file_path=LOG_PATH)
    main_logger = logging.getLogger(__name__)

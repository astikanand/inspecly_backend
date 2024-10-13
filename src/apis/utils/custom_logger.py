import logging


def get_logger(name):
    logger = logging.getLogger(name)
    log_level = logging.DEBUG
    logger.setLevel(log_level)

    # Log Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s\n%(message)s", datefmt="%d %b %Y %I:%M:%S %p")

    # Console Handler
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(log_level)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    # File Handler
    fileHandler = logging.FileHandler("nut_bolt.log")
    fileHandler.setLevel(log_level)
    fileHandler.setFormatter(formatter)
    # logger.addHandler(fileHandler)

    return logger

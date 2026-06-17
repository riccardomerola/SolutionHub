import logging

logging.basicConfig(filename=r"C:\BRETON\Appunti\Programmazione\Breton Solution Hub\Documents\00_logs.log", 
                    level=logging.INFO, 
                    format='%(asctime)s %(levelname)s - %(message)s', 
                    datefmt='%Y-%m-%d - %H:%M:%S'
                    )

def log(level, message):
    if level == "DEBUG":
        logging.debug(message)
    elif level == "INFO":
        logging.info(message)
    elif level == "WARNING":
        logging.warning(message)
    elif level == "ERROR":
        logging.error(message)
    elif level == "CRITICAL":
        logging.critical(message)
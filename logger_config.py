import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stdout)
logger = logging.getLogger()
fileHandler = logging.FileHandler("outlog.log", mode='w')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
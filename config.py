import logging
import sys
import yaml


logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stdout)
logger = logging.getLogger()
fileHandler = logging.FileHandler("outlog.log", mode='w')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


with open("config.yml", "r") as f:
    config = yaml.safe_load(f)
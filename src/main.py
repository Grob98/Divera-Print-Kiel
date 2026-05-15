import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import business.app_service

def setup_logging(global_path: str):
  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  fileHandler = TimedRotatingFileHandler(os.path.join(global_path, 'app.log'), when="midnight", backupCount=30)
  fileHandler.suffix = "%Y%m%d"
  fileHandler.setLevel(logging.DEBUG)
  fileHandler.setFormatter(formatter)

  consoleHandler = logging.StreamHandler()
  consoleHandler.setLevel(logging.DEBUG)
  consoleHandler.setFormatter(formatter)
  logger.addHandler(consoleHandler)
  logger.addHandler(fileHandler)

async def main(global_path: str):
  logging.info(f"Path set to: {global_path}")

  app_service = business.app_service.AppService(global_path)
  app_service.start()

if __name__ == "__main__":
  global_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  setup_logging(global_path)
  logging.info("Starting application...")

  asyncio.run(main(global_path))
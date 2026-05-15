import asyncio
from dotenv import load_dotenv
import logging
import os

from api.divera_connector import DiveraConnector
import business.app_service

def setup_logging():
  logging.basicConfig(filename='app.log', level=logging.DEBUG)
  consoleHandler = logging.StreamHandler()
  consoleHandler.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  consoleHandler.setFormatter(formatter)
  logging.getLogger('').addHandler(consoleHandler)

async def main():
  global_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  logging.info(f"Path set to: {global_path}")

  app_service = business.app_service.AppService(global_path)
  app_service.start()

  #connector = DiveraConnector()
  #await connector.start_polling()

  #stop_event = asyncio.Event()
  #await stop_event.wait()



if __name__ == "__main__":
  setup_logging()
  logging.info("Starting application...")

  asyncio.run(main())
import os
import logging



# path config
BASE_DIR = "/home/site/wwwroot"

# database config
DB_NAME = "test.db"
DATABASE_URL = f"sqlite:///{BASE_DIR}/db/{DB_NAME}"

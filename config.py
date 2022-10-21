from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN=os.getenv('TOKEN')
DBNAME=os.getenv('DBNAME')
USER=os.getenv('USR')
PASSWORD=os.getenv('PASSWORD')
HOST=os.getenv('HOST')

print(USER)
import os
import dotenv

dotenv.load_dotenv()

print(os.getenv("STORAGE_PATH"))
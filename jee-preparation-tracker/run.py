from dotenv import load_dotenv
import os
from app import app

dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv('.env')

print("DATABASE_URL:", os.getenv('DATABASE_URL'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

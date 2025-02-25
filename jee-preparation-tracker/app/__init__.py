from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# Configure Redis connection
redis_url = os.getenv('REDIS_URL')

# Use the Redis URL for connection
redis_client = redis.from_url(redis_url)

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri=redis_url,
    default_limits=["500 per day", "50 per hour"]
)

from app import routes, models
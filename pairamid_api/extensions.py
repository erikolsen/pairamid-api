from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS  # allow communication with react app
from flask_socketio import SocketIO
from flask_praetorian import Praetorian

migrate = Migrate()
db = SQLAlchemy()
socketio = SocketIO()
guard = Praetorian()

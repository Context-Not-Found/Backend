from contextlib import contextmanager
import bcrypt

import socketio
from sqlalchemy.schema import Column

from dependencies.db import get_db


sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
)


def verify_password(password: str, hashed_password: Column[str]):
    return bcrypt.checkpw(
        password.encode("utf-8"), str(hashed_password).encode("utf-8")
    )


get_db_manager = contextmanager(get_db)


points = [
    {"latitude": 28.797355, "longitude": 77.53686},
    {"latitude": 28.795077, "longitude": 77.54062},
    {"latitude": 28.796864, "longitude": 77.53910},
    {"latitude": 28.798355, "longitude": 77.53786},
    {"latitude": 28.794077, "longitude": 77.54162},
    {"latitude": 28.797864, "longitude": 77.53810},
    {"latitude": 28.796258, "longitude": 77.54236},
    {"latitude": 28.798915, "longitude": 77.54134},
    {"latitude": 28.797255, "longitude": 77.53676},
    {"latitude": 28.794977, "longitude": 77.54052},
    {"latitude": 28.796764, "longitude": 77.53900},
    {"latitude": 28.795198, "longitude": 77.54126},
    {"latitude": 28.797815, "longitude": 77.54024},
    {"latitude": 28.798455, "longitude": 77.53796},
    {"latitude": 28.794177, "longitude": 77.54172},
    {"latitude": 28.797964, "longitude": 77.53820},
    {"latitude": 28.796358, "longitude": 77.54246},
    {"latitude": 28.799015, "longitude": 77.54144}
    # ... add more points as needed
]

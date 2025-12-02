# src/db/init_db.py

from .session import engine, Base
from . import models  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("✅ สร้างตารางใน data/versioning.db เรียบร้อย")

########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\FLOWORK\flowork-gateway\migrations\env.py total lines 87 
########################################################################

from __future__ import annotations
import os
import pathlib
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
try:
    from flask import current_app
except Exception:
    current_app = None
config = context.config
if config.config_file_name is not None and os.path.exists(config.config_file_name):
    fileConfig(config.config_file_name)
DATA_DIR = os.environ.get("FLOWORK_GATEWAY_DATA_DIR", "/app/data")
try:
    pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"[Alembic][WARN] Failed to ensure data dir '{DATA_DIR}': {e}")
default_sqlite_url = f"sqlite:///{DATA_DIR.rstrip('/')}/gateway.db"
env_url = os.environ.get("DATABASE_URL")
flask_url = None
if current_app is not None:
    try:
        flask_url = current_app.config.get("SQLALCHEMY_DATABASE_URI")
    except Exception:
        flask_url = None
alembic_ini_url = config.get_main_option("sqlalchemy.url")
final_url = (
    (env_url or "").strip()
    or (flask_url or "").strip()
    or (alembic_ini_url or "").strip()
    or default_sqlite_url
)
if final_url.startswith("sqlite:///") and not final_url.startswith("sqlite:////"):
    print("[Alembic][INFO] Normalizing relative sqlite path to absolute under /app/data")
    rel = final_url.replace("sqlite:///", "", 1)
    if not rel.startswith("/"):
        final_url = f"sqlite:///{DATA_DIR.rstrip('/')}/{rel}"
    else:
        final_url = f"sqlite:///{rel}"
config.set_main_option("sqlalchemy.url", final_url.replace("%", "%%"))
target_metadata = None
if current_app is not None:
    try:
        target_metadata = current_app.extensions["migrate"].db.metadata
    except Exception:
        target_metadata = None
def run_migrations_offline() -> None:

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()
def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

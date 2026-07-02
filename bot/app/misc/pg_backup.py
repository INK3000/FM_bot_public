import asyncio
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import betterlogging as logging

from ..settings import settings

logger = logging.getLogger(__name__)

_TMP_DIR = Path("/tmp")
_STDERR_TRUNCATE = 500


def _conn_args() -> tuple[list[str], dict[str, str]]:
    """Parse DSN from settings and return (argv for -h/-p/-U/-d, env with PGPASSWORD)."""
    parsed = urlparse(settings.db.dsn)
    if not parsed.hostname or not parsed.username or not parsed.path:
        raise RuntimeError(f"Invalid POSTGRES DSN: {settings.db.dsn!r}")
    db_name = parsed.path.lstrip("/")
    port = str(parsed.port or 5432)

    argv = [
        "-h", parsed.hostname,
        "-p", port,
        "-U", parsed.username,
        "-d", db_name,
    ]
    env = {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "PGPASSWORD": parsed.password or "",
    }
    return argv, env


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


async def dump_db() -> Path:
    """Run pg_dump --clean --if-exists. Returns path to the .sql dump on success."""
    argv, env = _conn_args()
    out_path = _TMP_DIR / f"fm_backup_{_timestamp()}.sql"

    cmd = ["pg_dump", "--clean", "--if-exists", *argv, "-f", str(out_path)]
    logger.info("Running pg_dump -> %s", out_path)
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        out_path.unlink(missing_ok=True)
        msg = (stderr.decode(errors="replace") or "pg_dump failed").strip()
        raise RuntimeError(msg[:_STDERR_TRUNCATE])
    return out_path


async def restore_db(sql_path: Path) -> None:
    """Run psql -v ON_ERROR_STOP=1 -f <sql_path>. Raises RuntimeError on failure."""
    argv, env = _conn_args()
    cmd = ["psql", "-v", "ON_ERROR_STOP=1", *argv, "-f", str(sql_path)]
    logger.info("Running psql restore <- %s", sql_path)
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        msg = (stderr.decode(errors="replace") or "psql restore failed").strip()
        first_error = next(
            (line for line in msg.splitlines() if re.search(r"ERROR|FATAL", line)),
            msg,
        )
        raise RuntimeError(first_error[:_STDERR_TRUNCATE])

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


APP_NAME = "RETAILL_MCDA"
PORT = "8502"


def bundled_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def runtime_root() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_NAME
    return Path.home() / f".{APP_NAME.lower()}"


def copy_file(source: Path, target: Path, overwrite: bool = True) -> None:
    if not source.exists():
        return
    if target.exists() and not overwrite:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_tree(source: Path, target: Path, overwrite: bool = True) -> None:
    if not source.exists():
        return
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(source)
        copy_file(path, target / relative, overwrite=overwrite)


def prepare_runtime_files() -> Path:
    source_root = bundled_root()
    target_root = runtime_root()
    target_root.mkdir(parents=True, exist_ok=True)

    copy_file(source_root / "app.py", target_root / "app.py", overwrite=True)
    copy_file(source_root / "requirements.txt", target_root / "requirements.txt", overwrite=True)
    copy_tree(source_root / "core", target_root / "core", overwrite=True)
    copy_tree(source_root / ".streamlit", target_root / ".streamlit", overwrite=True)
    copy_tree(source_root / "logos", target_root / "logos", overwrite=True)
    copy_tree(source_root / "exports", target_root / "exports", overwrite=False)
    copy_tree(source_root / "data", target_root / "data", overwrite=False)

    return target_root / "app.py"


def main() -> None:
    app_path = prepare_runtime_files()
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    from streamlit.web import cli as streamlit_cli

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        PORT,
        "--server.headless",
        "true",
        "--global.developmentMode",
        "false",
        "--browser.gatherUsageStats",
        "false",
    ]
    raise SystemExit(streamlit_cli.main())


if __name__ == "__main__":
    main()

from pathlib import Path
import uuid
import shutil

def save_uploaded_file(uploaded_file, save_dir: Path, replace_path: str | None = None):
    if not uploaded_file:
        return replace_path or None

    save_dir.mkdir(parents=True, exist_ok=True)

    # If replacing, delete the old file first
    if replace_path and Path(replace_path).exists():
        try:
            Path(replace_path).unlink()
        except Exception:
            pass

    filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    save_path = save_dir / filename

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(save_path)

def delete_file(path: str):
    try:
        if path and Path(path).exists():
            Path(path).unlink()
    except Exception:
        pass

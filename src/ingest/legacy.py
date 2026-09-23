"""Legacy Office format readers (.doc, .ppt) via LibreOffice conversion."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _find_soffice() -> Path | None:
    for name in ("soffice", "soffice.exe"):
        found = shutil.which(name)
        if found:
            return Path(found)

    if sys.platform == "win32":
        candidates = [
            Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
            Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

    return None


def read_with_libreoffice(path: Path) -> str:
    """Convert legacy Office files to plain text using LibreOffice."""
    soffice = _find_soffice()
    if soffice is None:
        raise ValueError(
            f"Cannot read {path.suffix} files without LibreOffice. "
            "Install LibreOffice (https://www.libreoffice.org) or convert the file "
            f"to a modern format ({path.suffix}x)."
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [
                str(soffice),
                "--headless",
                "--convert-to",
                "txt:Text",
                "--outdir",
                tmpdir,
                str(path.resolve()),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip()
            raise ValueError(f"LibreOffice failed to convert {path.name}: {stderr}")

        txt_files = sorted(Path(tmpdir).glob("*.txt"))
        if not txt_files:
            raise ValueError(f"LibreOffice produced no text output for {path.name}")

        return txt_files[0].read_text(encoding="utf-8", errors="replace")

"""Extract the user-supplied paper versions without modifying their PDFs."""
import hashlib
import json
import sys
from pathlib import Path

from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r"C:\Users\User\Downloads\Documents")
out = ROOT / "extracted"
out.mkdir(exist_ok=True)
metadata = []
for paper in ("2604.21284v1", "2504.19413v1", "2501.13956v1"):
    path = SOURCE / f"{paper}.pdf"
    reader = PdfReader(path)
    pages = [page.extract_text(extraction_mode="layout") or "" for page in reader.pages]
    (out / f"{paper}.txt").write_text(
        "\n\n".join(f"=== PDF PAGE {i + 1} ===\n{text}" for i, text in enumerate(pages)),
        encoding="utf-8",
    )
    metadata.append({"id": paper, "source": str(path), "pages": len(pages),
                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                     "pdf_metadata": dict(reader.metadata or {})})
    print(paper, len(pages), "pages\n", pages[0][:4200], "\n")
(ROOT / "pdf-metadata.json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")

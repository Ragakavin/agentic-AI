import os
import hashlib
import time
from pathlib import Path
from typing import Any
from sqlalchemy.orm import Session
from backend.app.models.models import Invoice, AgentRun
from backend.app.core.config import settings

class IntakeAgent:
    """
    Agent 1 — Invoice Intake Agent
    Responsibilities:
    - Receive uploaded invoice
    - Identify file type
    - Validate file size & extension
    - Compute SHA-256 binary hash
    - Generate unique system invoice ID (e.g. INV-SYS-001)
    - Store initial invoice record
    """
    name = "Invoice Intake Agent"

    ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".webp"}
    MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

    def run(self, db: Session, file_path: Path, original_filename: str) -> dict[str, Any]:
        start_time = time.time()
        ext = file_path.suffix.lower()

        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file format: '{ext}'. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}")

        file_size = file_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File size ({file_size / (1024*1024):.1f} MB) exceeds maximum 25 MB limit.")

        # Compute SHA-256
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        doc_hash = sha256.hexdigest()

        # Generate unique invoice_id
        count = db.query(Invoice).count() + 1
        invoice_sys_id = f"INV-SYS-{count:03d}"

        # Determine formal file type
        file_type_map = {
            ".pdf": "PDF",
            ".png": "PNG",
            ".jpg": "JPG",
            ".jpeg": "JPEG",
            ".tiff": "TIFF",
            ".webp": "WEBP"
        }
        file_type = file_type_map.get(ext, "UNKNOWN")

        # Create Invoice record
        invoice = Invoice(
            invoice_id=invoice_sys_id,
            original_filename=original_filename,
            file_type=file_type,
            file_path=str(file_path),
            file_size_bytes=file_size,
            file_hash=doc_hash,
            status="received",
            risk_level="LOW"
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        execution_time_ms = int((time.time() - start_time) * 1000)

        output_data = {
            "invoice_id": invoice.invoice_id,
            "internal_db_id": invoice.id,
            "file_type": invoice.file_type,
            "file_size_bytes": file_size,
            "file_hash": doc_hash,
            "status": "received"
        }

        # Record Agent Run
        agent_run = AgentRun(
            invoice_id=invoice.id,
            agent_name=self.name,
            status="COMPLETED",
            execution_time_ms=execution_time_ms,
            input_data={"filename": original_filename, "path": str(file_path)},
            output_data=output_data
        )
        db.add(agent_run)
        db.commit()

        return output_data

intake_agent = IntakeAgent()

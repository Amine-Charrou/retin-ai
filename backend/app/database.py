"""
RetinAI Backend — SQLite Database Helper
Manages patients and analyses tables.
"""
import sqlite3
from contextlib import contextmanager
from backend.app.config import DATABASE_PATH


def init_db():
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                birthdate TEXT,
                gender TEXT DEFAULT 'M'
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                stage INTEGER NOT NULL,
                confidence REAL NOT NULL,
                referable INTEGER NOT NULL DEFAULT 0,
                urgency TEXT,
                image_path TEXT,
                heatmap_path TEXT,
                description TEXT,
                clinical_report TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            );
        """)


@contextmanager
def get_db():
    """Yield a database connection with row_factory set."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Patient CRUD ──────────────────────────────────────────────────────────────

def create_patient(patient_id: str, name: str, birthdate: str | None, gender: str):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO patients (id, name, birthdate, gender) VALUES (?, ?, ?, ?)",
            (patient_id, name, birthdate, gender)
        )


def list_patients():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
        return [dict(r) for r in rows]


def get_patient(patient_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
        return dict(row) if row else None


# ── Analysis CRUD ─────────────────────────────────────────────────────────────

def create_analysis(data: dict):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO analyses
               (id, patient_id, stage, confidence, referable, urgency,
                image_path, heatmap_path, description, clinical_report, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["id"], data["patient_id"], data["stage"], data["confidence"],
                data["referable"], data["urgency"], data["image_path"],
                data["heatmap_path"], data["description"], data["clinical_report"],
                data["created_at"]
            )
        )


def list_analyses():
    """Return analyses joined with patient info for the dashboard."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT a.*, p.name AS patient_name, p.gender AS patient_gender
            FROM analyses a
            LEFT JOIN patients p ON a.patient_id = p.id
            ORDER BY a.created_at DESC
        """).fetchall()
        return [dict(r) for r in rows]

"""
Cloudflare D1 Database Adapter
"""
import json
import sqlite3
from typing import Dict, Any, List, Optional
from app.server.events.schema import SDLCEvent, SDLCHealthImpact, SDLCRiskLevel, SDLCCategory, SDLCEventType


class D1DatabaseAdapter:
    """
    Adapter for Cloudflare D1 SQL database operations.
    Supports in-memory SQLite fallback for testing and local environment.
    """
    def __init__(self, db_connection=None):
        self._conn = db_connection or sqlite3.connect(":memory:")
        self._init_sqlite_tables()

    def _init_sqlite_tables(self):
        cursor = self._conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdlc_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                event_type TEXT NOT NULL,
                repository TEXT NOT NULL,
                branch TEXT,
                environment TEXT,
                actor_name TEXT,
                payload_json TEXT,
                score_delta REAL DEFAULT 0.0,
                risk_level TEXT DEFAULT 'LOW',
                message TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routine_history (
                id TEXT PRIMARY KEY,
                routine_name TEXT NOT NULL,
                executed_at TEXT NOT NULL,
                status TEXT NOT NULL,
                summary TEXT,
                details_json TEXT
            )
        """)
        self._conn.commit()

    def insert_event(self, event: SDLCEvent) -> bool:
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO sdlc_events (
                id, timestamp, source, category, event_type, repository, branch, environment, actor_name, payload_json, score_delta, risk_level, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.id,
            event.timestamp,
            event.source,
            event.category.value if hasattr(event.category, "value") else str(event.category),
            event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
            event.repository,
            event.branch,
            event.environment,
            event.actor.name if event.actor else "system",
            json.dumps(event.payload),
            event.health_impact.score_delta,
            event.health_impact.risk_level.value if hasattr(event.health_impact.risk_level, "value") else str(event.health_impact.risk_level),
            event.health_impact.message
        ))
        self._conn.commit()
        return True

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, source, category, event_type, repository, branch, environment, actor_name, score_delta, risk_level, message
            FROM sdlc_events ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r[0],
                "timestamp": r[1],
                "source": r[2],
                "category": r[3],
                "eventType": r[4],
                "repository": r[5],
                "branch": r[6],
                "environment": r[7],
                "actorName": r[8],
                "scoreDelta": r[9],
                "riskLevel": r[10],
                "message": r[11]
            })
        return result

-- Initial D1 SQL Schema Migration for Developer Workflow OS

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
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON sdlc_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_category ON sdlc_events(category);
CREATE INDEX IF NOT EXISTS idx_events_repository ON sdlc_events(repository);

CREATE TABLE IF NOT EXISTS routine_history (
    id TEXT PRIMARY KEY,
    routine_name TEXT NOT NULL,
    executed_at TEXT NOT NULL,
    status TEXT NOT NULL,
    summary TEXT,
    details_json TEXT
);

CREATE TABLE IF NOT EXISTS release_scores (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    score REAL NOT NULL,
    confidence TEXT NOT NULL,
    blockers_count INTEGER DEFAULT 0,
    details_json TEXT
);

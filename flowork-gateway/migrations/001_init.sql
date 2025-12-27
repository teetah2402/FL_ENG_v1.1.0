-- C:\FLOWORK\flowork-gateway\migrations\001_init.sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS engines (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  name TEXT NOT NULL,
  model_hint TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS engine_shares (
  engine_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('reader','runner')),
  created_at TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (engine_id, user_id),
  FOREIGN KEY (engine_id) REFERENCES engines(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  engine_id TEXT NOT NULL,
  intent TEXT,
  status TEXT NOT NULL CHECK (status IN ('queued','running','finishing','done','error','canceled')),
  ws_token TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (engine_id) REFERENCES engines(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS episodes (
  id TEXT PRIMARY KEY,
  engine_id TEXT NOT NULL,
  title TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (engine_id) REFERENCES engines(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS timeline (
  id TEXT PRIMARY KEY,
  episode_id TEXT NOT NULL,
  step_idx INTEGER NOT NULL,
  label TEXT,
  pointer JSON,          -- metadata only, no raw tokens
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE (episode_id, step_idx),
  FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sessions_engine ON sessions(engine_id);
CREATE INDEX IF NOT EXISTS idx_timeline_episode ON timeline(episode_id);
-- v0_1_0_00_core.sql
-- Core tables: schema_migrations / task_queue / task_run_log / sync_state

CREATE TABLE IF NOT EXISTS schema_migrations (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  version VARCHAR(64) NOT NULL UNIQUE,
  applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS task_queue (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_type VARCHAR(32) NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
  priority INT NOT NULL DEFAULT 100,
  payload_json JSON NOT NULL,
  run_after DATETIME NULL,
  locked_by VARCHAR(64) NULL,
  locked_at DATETIME NULL,
  retry_count INT NOT NULL DEFAULT 0,
  last_error TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  KEY idx_status_priority (status, priority, id),
  KEY idx_locked_at (locked_at),
  KEY idx_run_after (run_after)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS task_run_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id BIGINT NOT NULL,
  worker VARCHAR(64) NOT NULL,
  status VARCHAR(16) NOT NULL,
  started_at DATETIME NOT NULL,
  finished_at DATETIME NULL,
  error_type VARCHAR(32) NULL,
  error_message TEXT NULL,
  extra_json JSON NULL,

  KEY idx_task_id (task_id),
  KEY idx_started_at (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sync_state (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  platform VARCHAR(16) NOT NULL,
  account_id VARCHAR(128) NOT NULL,
  last_profile_snapshot_at DATETIME NULL,
  last_video_sync_at DATETIME NULL,
  last_comment_sync_at DATETIME NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uk_platform_account (platform, account_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

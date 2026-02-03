-- v0_1_1_00_ext.sql
-- SocialMonitor 数据库扩展 v1.1（在 v1.0 基础上增量升级）
-- 目标：更强的可回溯性、可扩展字段承载、以及多 worker 并发的“任务尝试(Attempt)”记录
-- 注意：全部是 ADD / CREATE，不做 DROP，保证可回滚与兼容
START TRANSACTION;

-- 1) 任务尝试表：把“每一次执行”单独记录出来（比 task_run_log 更结构化，方便统计成功率/耗时/重试）
CREATE TABLE IF NOT EXISTS task_attempt (
  attempt_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  task_id BIGINT NOT NULL,
  attempt_no INT NOT NULL DEFAULT 1,
  status VARCHAR(16) NOT NULL DEFAULT 'RUNNING',
  worker VARCHAR(64) NULL,
  started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at DATETIME NULL,
  duration_ms BIGINT NULL,
  error_type VARCHAR(32) NULL,
  error_message TEXT NULL,
  extra_json JSON NULL,

  KEY idx_task_attempt_task (task_id),
  KEY idx_task_attempt_status (status),
  KEY idx_task_attempt_started (started_at),

  CONSTRAINT fk_task_attempt_task
    FOREIGN KEY (task_id) REFERENCES task_queue(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2) 原始 HTTP 交换表：把接口请求/响应做“证据留存”，后续解析字段变更时可以重放
CREATE TABLE IF NOT EXISTS raw_http_exchange (
  exchange_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  platform VARCHAR(16) NOT NULL,
  task_id BIGINT NULL,
  request_url TEXT NOT NULL,
  request_method VARCHAR(8) NOT NULL DEFAULT 'GET',
  request_headers JSON NULL,
  request_body MEDIUMTEXT NULL,
  response_status INT NULL,
  response_headers JSON NULL,
  response_body MEDIUMTEXT NULL,
  fetched_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  trace_id VARCHAR(64) NULL,

  KEY idx_raw_http_platform_time (platform, fetched_at),
  KEY idx_raw_http_task (task_id),

  CONSTRAINT fk_raw_http_task
    FOREIGN KEY (task_id) REFERENCES task_queue(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3) master 层补充“首次/末次观测”字段：支持生命周期、平均/中位数等运营口径（不依赖 raw 表是否保留）
ALTER TABLE master_account
  ADD COLUMN first_seen_at DATETIME NULL AFTER signature,
  ADD COLUMN last_seen_at DATETIME NULL AFTER first_seen_at;

ALTER TABLE master_video
  ADD COLUMN first_seen_at DATETIME NULL AFTER share_count,
  ADD COLUMN last_seen_at DATETIME NULL AFTER first_seen_at;

ALTER TABLE master_comment
  ADD COLUMN first_seen_at DATETIME NULL AFTER like_count,
  ADD COLUMN last_seen_at DATETIME NULL AFTER first_seen_at;

-- 4) 任务队列补充“分组/批次”概念：方便我们按一次 Scheduler 生成的批次做追踪
ALTER TABLE task_queue
  ADD COLUMN batch_id VARCHAR(64) NULL AFTER payload_json,
  ADD COLUMN locked_at DATETIME NULL AFTER locked_by;

COMMIT;

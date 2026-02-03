-- v0_1_0_03_ai.sql
-- AI layer (traceability + artifact split)
-- NOTE:
-- 1) Do NOT use `USE ...` in migrations (DB is chosen by connection DB_NAME)
-- 2) Do NOT `SET NAMES` / `SET time_zone` here (should be handled by session/app config)

-- ================
-- master_video_analysis (AI短字段：可join，可聚合)
-- PK: (platform, video_id, biz_date)  -- 一天一份分析结果（符合“只重算昨天分区”）
-- ================
CREATE TABLE IF NOT EXISTS master_video_analysis (
  platform          VARCHAR(16)    NOT NULL,
  video_id          VARCHAR(128)   NOT NULL,
  biz_date          DATE           NOT NULL COMMENT '分析归属业务日(一般=昨天)',
  sentiment_score   DOUBLE         NULL COMMENT '情绪分(建议 -1~1 或 0~1)',
  sentiment_label   VARCHAR(16)    NULL COMMENT 'positive/neutral/negative',
  keywords_json     JSON           NULL COMMENT '关键词数组',
  topic_labels_json JSON           NULL COMMENT '主题标签数组',
  artifact_id       VARCHAR(64)    NULL COMMENT '关联 ai_run_artifacts.id',

  -- Traceability lineage (必填：可追溯)
  prompt_name       VARCHAR(64)    NOT NULL COMMENT 'prompts/active name',
  prompt_version    VARCHAR(16)    NOT NULL COMMENT 'prompts/versions/vX.Y.Z',
  model_name        VARCHAR(64)    NOT NULL COMMENT 'ollama model name',
  manifest_hash     CHAR(64)       NOT NULL COMMENT 'active_manifest.yaml hash',
  input_hash        CHAR(64)       NOT NULL COMMENT 'input payload hash',
  run_id            VARCHAR(64)    NOT NULL COMMENT 'brain run uuid',

  created_at        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (platform, video_id, biz_date),
  KEY idx_mva_biz_platform (biz_date, platform),
  KEY idx_mva_video (platform, video_id),
  KEY idx_mva_run (run_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='AI: video analysis short fields';

-- ================
-- ai_run_artifacts (AI长产物元信息：长JSON落盘，DB存路径+元数据)
-- id = artifact_id (UUID / deterministic id)
-- ================
CREATE TABLE IF NOT EXISTS ai_run_artifacts (
  id               VARCHAR(64)    NOT NULL COMMENT 'artifact_id',
  run_id            VARCHAR(64)    NOT NULL COMMENT 'brain run uuid',
  platform          VARCHAR(16)    NOT NULL,
  video_id          VARCHAR(128)   NOT NULL,
  biz_date          DATE           NOT NULL,

  prompt_name       VARCHAR(64)    NOT NULL,
  prompt_version    VARCHAR(16)    NOT NULL,
  model_name        VARCHAR(64)    NOT NULL,
  manifest_hash     CHAR(64)       NOT NULL,
  input_hash        CHAR(64)       NOT NULL,

  artifact_path     VARCHAR(512)   NOT NULL COMMENT '落盘路径(SSD hot区)',
  artifact_sha256   CHAR(64)       NULL COMMENT '文件sha256(可选)',
  artifact_bytes    BIGINT         NULL COMMENT '文件大小(可选)',

  created_at        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  KEY idx_ara_run (run_id),
  KEY idx_ara_vid (platform, video_id, biz_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='AI: run artifacts metadata only';

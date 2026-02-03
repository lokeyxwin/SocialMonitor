-- v0_1_0_02_master.sql
-- Master layer (upsert latest)
-- NOTE:
-- 1) Do NOT use `USE ...` in migrations (DB is chosen by connection DB_NAME)
-- 2) Do NOT `SET NAMES` / `SET time_zone` here (should be handled by session/app config)

-- ================
-- master_account (账号最新画像)
-- Primary Key: (platform, account_id)
-- ================
CREATE TABLE IF NOT EXISTS master_account (
  platform        VARCHAR(16)   NOT NULL,
  account_id      VARCHAR(128)  NOT NULL,
  latest_biz_date DATE          NULL COMMENT '最近一次快照业务日',
  follower_count  BIGINT        NULL,
  like_count      BIGINT        NULL,
  post_count      INT           NULL,
  rule_version    VARCHAR(16)   NOT NULL DEFAULT 'v0.0.0' COMMENT '清洗规则版本',
  updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (platform, account_id),
  KEY idx_ma_bizdate (platform, latest_biz_date),
  KEY idx_ma_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Master: account latest';

-- ================
-- master_video (视频最新状态)
-- Primary Key: (platform, video_id)
-- ================
CREATE TABLE IF NOT EXISTS master_video (
  platform       VARCHAR(16)   NOT NULL,
  video_id       VARCHAR(128)  NOT NULL,
  account_id     VARCHAR(128)  NOT NULL,
  create_time    DATETIME      NULL,
  desc_text      TEXT          NULL,
  like_count     BIGINT        NULL,
  comment_count  BIGINT        NULL,
  share_count    BIGINT        NULL,
  rule_version   VARCHAR(16)   NOT NULL DEFAULT 'v0.0.0',
  updated_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (platform, video_id),

  -- 供增量构建 mart / 查询账号近期视频
  KEY idx_mv_account_time (platform, account_id, create_time),

  -- 供“最近7天视频才追评论”的筛选（按更新时间也很常用）
  KEY idx_mv_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Master: video latest';

-- ================
-- master_comment (评论主表：受窗口策略控制，避免无限膨胀)
-- Primary Key: (platform, comment_id)
-- ================
CREATE TABLE IF NOT EXISTS master_comment (
  platform      VARCHAR(16)   NOT NULL,
  comment_id    VARCHAR(128)  NOT NULL,
  video_id      VARCHAR(128)  NOT NULL,
  account_id    VARCHAR(128)  NOT NULL,
  content_text  TEXT          NULL,
  like_count    BIGINT        NULL,
  create_time   DATETIME      NULL,
  window_type   VARCHAR(32)   NOT NULL DEFAULT 'UNKNOWN' COMMENT 'NEW_VIDEO_TOP1000 / RECENT7D_24H / ...',
  rule_version  VARCHAR(16)   NOT NULL DEFAULT 'v0.0.0',
  updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (platform, comment_id),

  -- 常用：按视频拉评论时间线 / 追新增评论
  KEY idx_mc_video_time (platform, video_id, create_time),

  -- 常用：按账号聚合舆情（视频作者维度）
  KEY idx_mc_account (platform, account_id),

  KEY idx_mc_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Master: comment (window-limited)';

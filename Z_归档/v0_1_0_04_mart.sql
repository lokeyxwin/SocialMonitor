-- v0_1_0_04_mart.sql
-- Mart layer (daily rebuild yesterday)
-- NOTE:
-- 1) Do NOT use `USE ...` in migrations (DB is chosen by connection DB_NAME)
-- 2) Do NOT `SET NAMES` / `SET time_zone` here (should be handled by session/app config)

-- ================
-- mart_daily_account_metrics (账号日指标)
-- PK: (biz_date, platform, account_id)
-- ================
CREATE TABLE IF NOT EXISTS mart_daily_account_metrics (
  biz_date            DATE          NOT NULL,
  platform            VARCHAR(16)   NOT NULL,
  account_id          VARCHAR(128)  NOT NULL,

  follower_count      BIGINT        NULL,
  follower_delta      BIGINT        NULL,
  like_count          BIGINT        NULL,
  like_delta          BIGINT        NULL,

  new_video_count     INT           NULL,
  new_comment_count   BIGINT        NULL,

  sentiment_pos_cnt   INT           NULL,
  sentiment_neu_cnt   INT           NULL,
  sentiment_neg_cnt   INT           NULL,

  updated_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (biz_date, platform, account_id),
  KEY idx_mdam_date_platform (biz_date, platform),
  KEY idx_mdam_platform_account (platform, account_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Mart: daily account metrics';

-- ================
-- mart_daily_video_metrics (视频日指标：爆款/内容表现)
-- PK: (biz_date, platform, video_id)
-- ================
CREATE TABLE IF NOT EXISTS mart_daily_video_metrics (
  biz_date           DATE          NOT NULL,
  platform           VARCHAR(16)   NOT NULL,
  video_id           VARCHAR(128)  NOT NULL,
  account_id         VARCHAR(128)  NOT NULL,

  create_time        DATETIME      NULL,
  like_count         BIGINT        NULL,
  comment_count      BIGINT        NULL,
  share_count        BIGINT        NULL,

  sentiment_label    VARCHAR(16)   NULL,
  sentiment_score    DOUBLE        NULL,

  updated_at         DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (biz_date, platform, video_id),
  KEY idx_mdvm_date_platform_account (biz_date, platform, account_id),
  KEY idx_mdvm_platform_video (platform, video_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Mart: daily video metrics';

-- ================
-- mart_daily_topic_keywords (每天关键词/主题榜)
-- PK: (biz_date, platform, account_id, keyword)
-- ================
CREATE TABLE IF NOT EXISTS mart_daily_topic_keywords (
  biz_date      DATE          NOT NULL,
  platform      VARCHAR(16)   NOT NULL,
  account_id    VARCHAR(128)  NOT NULL,
  keyword       VARCHAR(128)  NOT NULL,
  freq          INT           NOT NULL DEFAULT 0,

  updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (biz_date, platform, account_id, keyword),
  KEY idx_mdtk_date_platform (biz_date, platform),
  KEY idx_mdtk_platform_keyword (platform, keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Mart: daily keywords ranking';

-- ================
-- mart_daily_sentiment_summary (每天情绪汇总)
-- PK: (biz_date, platform, account_id)
-- ================
CREATE TABLE IF NOT EXISTS mart_daily_sentiment_summary (
  biz_date      DATE          NOT NULL,
  platform      VARCHAR(16)   NOT NULL,
  account_id    VARCHAR(128)  NOT NULL,

  pos_cnt       INT           NOT NULL DEFAULT 0,
  neu_cnt       INT           NOT NULL DEFAULT 0,
  neg_cnt       INT           NOT NULL DEFAULT 0,
  avg_score     DOUBLE        NULL,

  updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (biz_date, platform, account_id),
  KEY idx_mdss_date_platform (biz_date, platform)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Mart: daily sentiment summary';

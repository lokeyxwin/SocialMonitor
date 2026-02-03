-- v0_1_0_01_raw.sql
-- Raw layer (append-only) + idempotency via hash_id PK
-- NOTE:
-- 1) Do NOT use `USE ...` in migrations (DB is chosen by connection DB_NAME)
-- 2) Do NOT `SET NAMES` / `SET time_zone` here (should be handled by session/app config)

-- ================
-- raw_profile_snapshot (主页快照：窗口内仅一次)
-- hash_id = md5(platform + account_id + biz_date)
-- ================
CREATE TABLE IF NOT EXISTS raw_profile_snapshot (
  hash_id         CHAR(32)      NOT NULL COMMENT 'md5(platform + account_id + biz_date)',
  platform        VARCHAR(16)   NOT NULL COMMENT 'douyin/xhs',
  account_id      VARCHAR(128)  NOT NULL COMMENT '账号ID',
  biz_date        DATE          NOT NULL COMMENT '业务日期(北京时间)',
  captured_at     DATETIME      NOT NULL COMMENT '抓取时间(窗口内)',
  follower_count  BIGINT        NULL COMMENT '粉丝数(已规范化)',
  like_count      BIGINT        NULL COMMENT '获赞/点赞总量(如平台提供)',
  post_count      INT           NULL COMMENT '作品数(如平台提供)',
  raw_json        JSON          NULL COMMENT '原始字段兜底',
  ingested_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  PRIMARY KEY (hash_id),
  KEY idx_rps_lookup (platform, account_id, biz_date),
  KEY idx_rps_ingest (ingested_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Raw: profile snapshot (append-only)';

-- ================
-- raw_video (视频明细：增量抓取)
-- hash_id = md5(platform + video_id)
-- ================
CREATE TABLE IF NOT EXISTS raw_video (
  hash_id        CHAR(32)      NOT NULL COMMENT 'md5(platform + video_id)',
  platform       VARCHAR(16)   NOT NULL COMMENT 'douyin/xhs',
  video_id       VARCHAR(128)  NOT NULL COMMENT '视频ID',
  account_id     VARCHAR(128)  NOT NULL COMMENT '作者账号ID',
  create_time    DATETIME      NULL COMMENT '发布时间(解析失败可为空)',
  desc_text      TEXT          NULL COMMENT '标题/文案',
  like_count     BIGINT        NULL COMMENT '点赞数(已规范化)',
  comment_count  BIGINT        NULL COMMENT '评论数(已规范化)',
  share_count    BIGINT        NULL COMMENT '分享数(已规范化)',
  raw_json       JSON          NULL COMMENT '原始字段兜底',
  ingested_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  PRIMARY KEY (hash_id),

  -- 供 “账号维度增量 + create_time 边界 + video_id 窗口兜底” 查询更顺
  KEY idx_rv_inc (platform, account_id, create_time, video_id),

  -- 单视频定位
  KEY idx_rv_video (platform, video_id),

  KEY idx_rv_ingest (ingested_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Raw: video (append-only)';

-- ================
-- raw_comment (评论明细：按规则限窗抓取)
-- hash_id = md5(platform + comment_id)
-- ================
CREATE TABLE IF NOT EXISTS raw_comment (
  hash_id       CHAR(32)      NOT NULL COMMENT 'md5(platform + comment_id)',
  platform      VARCHAR(16)   NOT NULL COMMENT 'douyin/xhs',
  comment_id    VARCHAR(128)  NOT NULL COMMENT '评论ID',
  video_id      VARCHAR(128)  NOT NULL COMMENT '所属视频ID',
  account_id    VARCHAR(128)  NOT NULL COMMENT '作者账号ID(视频作者)',
  user_name     VARCHAR(255)  NULL COMMENT '评论者昵称(可选)',
  content_text  TEXT          NULL COMMENT '评论文本',
  like_count    BIGINT        NULL COMMENT '评论点赞数(已规范化)',
  create_time   DATETIME      NULL COMMENT '评论时间(解析失败可为空)',
  raw_json      JSON          NULL COMMENT '原始字段兜底',
  ingested_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  PRIMARY KEY (hash_id),

  -- 供 “新视频抓前N评论 / 存量视频追24h新增 / 按视频+时间范围” 查询
  KEY idx_rc_video_time (platform, video_id, create_time, comment_id),

  -- 单评论定位
  KEY idx_rc_comment (platform, comment_id),

  KEY idx_rc_ingest (ingested_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='Raw: comment (append-only)';

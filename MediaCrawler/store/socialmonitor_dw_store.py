# 文件路径: MediaCrawler/store/socialmonitor_dw_store.py
import datetime
from typing import Dict, Optional
from sqlalchemy import text
from database.db import get_async_engine # 关键：用全局引擎
from tools import utils

def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def _to_datetime(ts) -> Optional[datetime.datetime]:
    if ts is None: return None
    try:
        ts_int = int(ts)
        if ts_int > 10_000_000_000: ts_int = ts_int // 1000
        return datetime.datetime.fromtimestamp(ts_int)
    except: return None

async def upsert_monitor_dy_video_daily(content_item: Dict):
    now = datetime.datetime.now()
    # 每日快照表：记录视频当天的点赞评论数
    # 【修改点 1】SQL里加上 create_time
    sql = text(
        """
        INSERT INTO monitor_dy_video_daily (
            aweme_id, user_id, title, create_time, liked_count, comment_count, share_count, collected_count, record_date
        ) VALUES (
            :aweme_id, :user_id, :title, :create_time, :liked_count, :comment_count, :share_count, :collected_count, :record_date
        )
        ON DUPLICATE KEY UPDATE
            user_id = VALUES(user_id),
            title = VALUES(title),
            create_time = VALUES(create_time),
            liked_count = VALUES(liked_count),
            comment_count = VALUES(comment_count),
            share_count = VALUES(share_count),
            collected_count = VALUES(collected_count)
        """
    )

    params = {
        "aweme_id": str(content_item.get("aweme_id", "")),
        "user_id": str(content_item.get("user_id", "")),
        "title": (content_item.get("title") or "")[:512],
        # 【修改点 2】把时间戳转成标准时间格式
        "create_time": _to_datetime(content_item.get("create_time")), 
        "liked_count": _to_int(content_item.get("liked_count")),
        "comment_count": _to_int(content_item.get("comment_count")),
        "share_count": _to_int(content_item.get("share_count")),
        "collected_count": _to_int(content_item.get("collected_count")),
        "record_date": now.date(),
    }

    # 使用全局连接池
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(sql, params)

async def insert_search_dy_content(content_item: Dict):
    """
    插入搜索结果（已开启去重模式：数据库有的直接跳过）
    """
    keyword = (content_item.get("source_keyword") or "").strip()
    if not keyword: return

    # 【修改点】把 INSERT INTO 改为 INSERT IGNORE INTO
    # 含义：如果 (keyword, aweme_id) 冲突，就直接忽略这条数据，不报错，也不更新
    sql = text("""
        INSERT IGNORE INTO search_dy_content (
            keyword, aweme_id, user_id, sec_uid, title, 
            liked_count, comment_count, share_count, collected_count, is_visible,
            publish_time, crawled_at
        ) VALUES (
            :keyword, :aweme_id, :user_id, :sec_uid, :title, 
            :liked_count, :comment_count, :share_count, :collected_count, :is_visible,
            :publish_time, :crawled_at
        )
    """)

    params = {
        # ... (参数部分不用变，和你之前的一样) ...
        "keyword": keyword[:64],
        "aweme_id": str(content_item.get("aweme_id", "")),
        "user_id": str(content_item.get("user_id", "")),
        "sec_uid": str(content_item.get("sec_uid", "")),
        "title": content_item.get("title") or "",
        "liked_count": _to_int(content_item.get("liked_count")),
        "comment_count": _to_int(content_item.get("comment_count")),
        "share_count": _to_int(content_item.get("share_count")),
        "collected_count": _to_int(content_item.get("collected_count")),
        "is_visible": 1,
        "publish_time": _to_datetime(content_item.get("create_time")),
        "crawled_at": datetime.datetime.now(),
    }

    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(sql, params)

async def upsert_monitor_dy_creator_daily(creator_item: Dict):
    now = datetime.datetime.now()
    sql = text("""
        INSERT INTO monitor_dy_creator_daily (
            user_id, sec_uid, nickname, fans_count, follow_count, total_favorited, publish_count, record_date, crawled_at
        ) VALUES (
            :user_id, :sec_uid, :nickname, :fans_count, :follow_count, :total_favorited, :publish_count, :record_date, :crawled_at
        )
        ON DUPLICATE KEY UPDATE
            sec_uid = VALUES(sec_uid), nickname = VALUES(nickname), fans_count = VALUES(fans_count),
            follow_count = VALUES(follow_count), total_favorited = VALUES(total_favorited),
            publish_count = VALUES(publish_count), crawled_at = VALUES(crawled_at)
    """)
    params = {
        "user_id": str(creator_item.get("user_id", "")),
        "sec_uid": str(creator_item.get("sec_uid", ""))[:128],
        "nickname": str(creator_item.get("nickname", ""))[:128],
        "fans_count": _to_int(creator_item.get("fans")),
        "follow_count": _to_int(creator_item.get("follows")),
        "total_favorited": _to_int(creator_item.get("interaction")),
        "publish_count": _to_int(creator_item.get("videos_count")),
        "record_date": now.date(),
        "crawled_at": now,
    }
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(sql, params)


async def upsert_monitor_dy_comment(comment_item: Dict):
    """
    存储单条评论到监控表 (已添加 reply_to_user_id)
    """
    # 【修改点1】SQL 增加 reply_to_user_id
    sql = text("""
        INSERT INTO monitor_dy_comment (
            comment_id, aweme_id, user_id, sec_uid, nickname, content,
            like_count, sub_comment_count, create_time, 
            parent_comment_id, reply_to_user_id, crawled_at
        ) VALUES (
            :comment_id, :aweme_id, :user_id, :sec_uid, :nickname, :content,
            :like_count, :sub_comment_count, :create_time, 
            :parent_comment_id, :reply_to_user_id, :crawled_at
        )
        ON DUPLICATE KEY UPDATE
            like_count = VALUES(like_count),
            sub_comment_count = VALUES(sub_comment_count),
            nickname = VALUES(nickname),
            crawled_at = VALUES(crawled_at)
    """)
    
    params = {
        "comment_id": str(comment_item.get("comment_id", "")),
        "aweme_id": str(comment_item.get("aweme_id", "")),
        "user_id": str(comment_item.get("user_id", "")),
        "sec_uid": str(comment_item.get("sec_uid", "")),
        "nickname": str(comment_item.get("nickname", "") or "")[:128],
        "content": str(comment_item.get("content", "") or ""),
        "like_count": _to_int(comment_item.get("like_count")),
        "sub_comment_count": _to_int(comment_item.get("sub_comment_count")),
        "create_time": _to_datetime(comment_item.get("create_time")),
        "parent_comment_id": str(comment_item.get("parent_comment_id", "0")),
        
        # 【修改点2】从字典获取值
        "reply_to_user_id": str(comment_item.get("reply_to_user_id", "")),
        
        "crawled_at": datetime.datetime.now()
    }

    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(sql, params)
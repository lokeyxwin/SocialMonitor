# 文件路径: MediaCrawler/store/douyin/socialmonitor_dw_store.py
import re
import datetime
from typing import Dict
from sqlalchemy import text
from database.db import get_async_engine
from tools import utils

# === 辅助工具函数 ===

def _to_int(val):
    """安全转换为整数"""
    if val is None or val == "":
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

def _to_datetime(timestamp):
    """
    【核心修复】智能识别 秒(10位) 和 毫秒(13位)
    """
    if not timestamp:
        return datetime.datetime.now()
    try:
        # 1. 如果已经是时间对象，直接返回
        if isinstance(timestamp, (datetime.datetime, datetime.date)):
            return timestamp
        
        # 2. 转为整数
        ts = int(timestamp)
        
        # 3. 智能判断：如果数值很大(大于100亿)，说明是毫秒，需要除以1000
        # 现在的秒级时间戳大约是 17亿 (10位)，毫秒级是 17000亿 (13位)
        if ts > 10000000000: 
            ts = ts / 1000
            
        return datetime.datetime.fromtimestamp(ts)
    except:
        return datetime.datetime.now()

def _extract_topics(text_content):
    """提取 #话题"""
    if not text_content: return ""
    topics = re.findall(r"#(\S+)", str(text_content))
    return ",".join(topics)[:512]

def _extract_mentions(text_content):
    """提取 @用户"""
    if not text_content: return ""
    mentions = re.findall(r"@(\S+?)(?=\s|$)", str(text_content))
    return ",".join(mentions)[:512]

# === 1. 搜索入库 ===

async def insert_search_dy_content(content_item: Dict):
    keyword = (content_item.get("source_keyword") or "").strip()
    if not keyword: return

    desc = content_item.get("title", "") or ""
    aweme_id = str(content_item.get("aweme_id", ""))
    sec_uid = str(content_item.get("sec_uid", ""))

    # 提取新字段
    topics = _extract_topics(desc)
    mentions = _extract_mentions(desc)
    
    music_info = content_item.get("music", {})
    bgm_name = music_info.get("title", "") if isinstance(music_info, dict) else ""
    
    aweme_url = content_item.get("aweme_url") or f"https://www.douyin.com/video/{aweme_id}"
    author_url = f"https://www.douyin.com/user/{sec_uid}"
    
    # 这里的 nickname 有时候在上游叫 nickname，有时候在 user 字典里
    nickname = content_item.get("nickname", "")

    # 【注意】根据截图，你的 search 表确实缺 aweme_url，下面 SQL 会报错
    # 请务必执行第二步的 SQL 补丁！
    sql = text("""
        INSERT INTO search_dy_content (
            keyword, aweme_id, user_id, sec_uid, title, 
            liked_count, comment_count, share_count, collected_count, 
            aweme_url, author_url, nickname, ip_location,
            topics, bgm_name, mentions,
            is_visible, publish_time, crawled_at
        ) VALUES (
            :keyword, :aweme_id, :user_id, :sec_uid, :title, 
            :liked_count, :comment_count, :share_count, :collected_count, 
            :aweme_url, :author_url, :nickname, :ip_location,
            :topics, :bgm_name, :mentions,
            :is_visible, :publish_time, :crawled_at
        )
        ON DUPLICATE KEY UPDATE
            keyword = VALUES(keyword), 
            liked_count = VALUES(liked_count),
            comment_count = VALUES(comment_count),
            share_count = VALUES(share_count),
            collected_count = VALUES(collected_count),
            crawled_at = VALUES(crawled_at),
            nickname = VALUES(nickname),
            ip_location = VALUES(ip_location),
            topics = VALUES(topics),
            bgm_name = VALUES(bgm_name),
            mentions = VALUES(mentions),
            author_url = VALUES(author_url),
            aweme_url = VALUES(aweme_url)
    """)

    params = {
        "keyword": keyword[:64],
        "aweme_id": aweme_id,
        "user_id": str(content_item.get("user_id", "")),
        "sec_uid": sec_uid,
        "title": desc,
        "liked_count": _to_int(content_item.get("liked_count")),
        "comment_count": _to_int(content_item.get("comment_count")),
        "share_count": _to_int(content_item.get("share_count")),
        "collected_count": _to_int(content_item.get("collected_count")),
        "aweme_url": aweme_url,
        "author_url": author_url,
        "nickname": nickname,
        "ip_location": content_item.get("ip_location", ""),
        "topics": topics,
        "bgm_name": bgm_name[:255],
        "mentions": mentions,
        "is_visible": 1,
        "publish_time": _to_datetime(content_item.get("create_time")),
        "crawled_at": datetime.datetime.now(),
    }

    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(sql, params)


# === 2. 视频监控入库 (已修正字段名) ===

async def upsert_monitor_dy_video_daily(content_item: Dict):
    aweme_id = str(content_item.get("aweme_id", ""))
    if not aweme_id: return

    desc = content_item.get("title", "") or ""
    topics = _extract_topics(desc)
    mentions = _extract_mentions(desc)
    music_info = content_item.get("music", {})
    bgm_name = music_info.get("title", "") if isinstance(music_info, dict) else ""
    aweme_url = content_item.get("aweme_url") or f"https://www.douyin.com/video/{aweme_id}"
    today = datetime.date.today()

    # 【修正】snapshot_date -> record_date
    sql = text("""
        INSERT INTO monitor_dy_video_daily (
            aweme_id, user_id, title, 
            liked_count, comment_count, share_count, collected_count,
            topics, bgm_name, mentions, ip_location, video_url,
            record_date, create_time, publish_time
        ) VALUES (
            :aweme_id, :user_id, :title, 
            :liked_count, :comment_count, :share_count, :collected_count,
            :topics, :bgm_name, :mentions, :ip_location, :video_url,
            :record_date, :create_time, :publish_time
        )
        ON DUPLICATE KEY UPDATE
            liked_count = VALUES(liked_count),
            comment_count = VALUES(comment_count),
            share_count = VALUES(share_count),
            collected_count = VALUES(collected_count),
            create_time = VALUES(create_time),
            
            topics = VALUES(topics),
            bgm_name = VALUES(bgm_name),
            mentions = VALUES(mentions),
            ip_location = VALUES(ip_location),
            video_url = VALUES(video_url) 
    """)

    params = {
        "aweme_id": aweme_id,
        "user_id": str(content_item.get("user_id", "")),
        "title": desc,
        "liked_count": _to_int(content_item.get("liked_count")),
        "comment_count": _to_int(content_item.get("comment_count")),
        "share_count": _to_int(content_item.get("share_count")),
        "collected_count": _to_int(content_item.get("collected_count")),
        "topics": topics,
        "bgm_name": bgm_name[:255],
        "mentions": mentions,
        "ip_location": content_item.get("ip_location", ""),
        "video_url": aweme_url,
        "record_date": today,  # 对应 DB 的 record_date
        "create_time": datetime.datetime.now(),
        "publish_time": _to_datetime(content_item.get("create_time")),
    }

    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(sql, params)


# === 3. 评论入库 (无需修改) ===
async def upsert_monitor_dy_comment(comment_item: Dict):
    cid = str(comment_item.get("comment_id", ""))
    if not cid: return

    aweme_id = str(comment_item.get("aweme_id", ""))
    video_url = f"https://www.douyin.com/video/{aweme_id}"
    content = comment_item.get("content", "")
    keywords_extracted = "" 

    sql = text("""
        INSERT IGNORE INTO monitor_dy_comment (
            comment_id, aweme_id, video_url, user_id, sec_uid, nickname, 
            content, keywords_extracted,
            like_count, sub_comment_count, 
            create_time, crawled_at, 
            parent_comment_id, reply_to_user_id
        ) VALUES (
            :comment_id, :aweme_id, :video_url, :user_id, :sec_uid, :nickname, 
            :content, :keywords_extracted,
            :like_count, :sub_comment_count, 
            :create_time, :crawled_at, 
            :parent_comment_id, :reply_to_user_id
        )
    """)

    params = {
        "comment_id": cid,
        "aweme_id": aweme_id,
        "video_url": video_url,
        "user_id": str(comment_item.get("user_id", "")),
        "sec_uid": str(comment_item.get("sec_uid", "")),
        "nickname": comment_item.get("nickname", ""),
        "content": content,
        "keywords_extracted": keywords_extracted,
        "like_count": _to_int(comment_item.get("like_count")),
        "sub_comment_count": _to_int(comment_item.get("sub_comment_count")),
        "create_time": _to_datetime(comment_item.get("create_time")),
        "crawled_at": datetime.datetime.now(),
        "parent_comment_id": str(comment_item.get("parent_comment_id", "0")),
        "reply_to_user_id": str(comment_item.get("reply_to_user_id", "")),
    }

    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(sql, params)

# === 4. 博主日报入库 (已修正字段名) ===

async def upsert_monitor_dy_creator_daily(creator_item: Dict):
    user_id = str(creator_item.get("user_id", ""))
    if not user_id: return
    
    today = datetime.date.today()
    sec_uid = str(creator_item.get("sec_uid", ""))
    home_url = f"https://www.douyin.com/user/{sec_uid}" if sec_uid else ""
    
    age = _to_int(creator_item.get("age", 0))
    gender = _to_int(creator_item.get("gender", 0))

    # 【修正】
    # like_count -> total_favorited
    # video_count -> publish_count
    # snapshot_date -> record_date
    sql = text("""
        INSERT INTO monitor_dy_creator_daily (
            user_id, sec_uid, nickname, 
            fans_count, follow_count, total_favorited, publish_count,
            signature, ip_location, age, gender, mcn_name, avatar_url, home_url,
            record_date, crawled_at
        ) VALUES (
            :user_id, :sec_uid, :nickname, 
            :fans_count, :follow_count, :total_favorited, :publish_count,
            :signature, :ip_location, :age, :gender, :mcn_name, :avatar_url, :home_url,
            :record_date, :crawled_at
        )
        ON DUPLICATE KEY UPDATE
            fans_count      = VALUES(fans_count),
            follow_count    = VALUES(follow_count),
            total_favorited = VALUES(total_favorited),
            publish_count   = VALUES(publish_count),
            crawled_at      = VALUES(crawled_at),
            
            signature   = VALUES(signature),
            ip_location = VALUES(ip_location),
            age         = VALUES(age),
            gender      = VALUES(gender),
            mcn_name    = VALUES(mcn_name),
            avatar_url  = VALUES(avatar_url),
            home_url    = VALUES(home_url)
    """)

    params = {
        "user_id": user_id,
        "sec_uid": sec_uid,
        "nickname": creator_item.get("nickname", ""),
        "fans_count": _to_int(creator_item.get("fans")),
        "follow_count": _to_int(creator_item.get("follows")),
        "total_favorited": _to_int(creator_item.get("interaction")), # 对应 total_favorited
        "publish_count": _to_int(creator_item.get("videos_count")), # 对应 publish_count
        "signature": creator_item.get("signature", ""),
        "ip_location": creator_item.get("ip_location", ""),
        "age": age,
        "gender": gender,
        "mcn_name": creator_item.get("mcn_name", ""),
        "avatar_url": creator_item.get("avatar", ""),
        "home_url": home_url,
        "record_date": today, # 对应 record_date
        "crawled_at": datetime.datetime.now(),
    }

    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(sql, params)
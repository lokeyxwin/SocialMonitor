# -*- coding: utf-8 -*-
# 文件路径: MediaCrawler/store/douyin/__init__.py
from typing import List, Dict
import config
from var import source_keyword_var
from tools import utils

# 1. 媒体下载 (存图片/视频文件)
from .douyin_store_media import *

# 2. 数据库存储 (你写的新逻辑)
from .socialmonitor_dw_store import (
    insert_search_dy_content,
    upsert_monitor_dy_video_daily,
    upsert_monitor_dy_comment,
    upsert_monitor_dy_creator_daily
)

# ================= 数据清洗辅助函数 =================

def _extract_note_image_list(aweme_detail: Dict) -> List[str]:
    images: List[Dict] = aweme_detail.get("images", [])
    if not images: return []
    return [img.get("url_list", [])[-1] for img in images if img.get("url_list")]

def _extract_content_cover_url(aweme_detail: Dict) -> str:
    video = aweme_detail.get("video", {})
    cover = video.get("raw_cover", {}) or video.get("origin_cover", {})
    urls = cover.get("url_list", [])
    return urls[1] if len(urls) > 1 else ""

def _extract_video_download_url(aweme_detail: Dict) -> str:
    video = aweme_detail.get("video", {})
    urls = video.get("play_addr", {}).get("url_list", [])
    return urls[-1] if urls else ""

def _extract_music_download_url(aweme_detail: Dict) -> str:
    return aweme_detail.get("music", {}).get("play_url", {}).get("uri", "")

# ================= 核心：数据分发逻辑 =================

async def update_douyin_aweme(aweme_item: Dict):
    """
    爬虫拿到数据后，会调用这个函数。
    我们在这里把数据清洗好，传给 socialmonitor_dw_store
    """
    utils.logger.info(f"🏭 [库管员] 收到数据包，正在拆包清洗，准备写入 MySQL...")
    aweme_id = aweme_item.get("aweme_id")
    user_info = aweme_item.get("author", {})
    interact = aweme_item.get("statistics", {})
    
    # 组装基础数据包 (SocialMonitorStore 会再次提取高级字段如话题等)
    save_item = {
        "aweme_id": aweme_id,
        "aweme_type": str(aweme_item.get("aweme_type")),
        "title": aweme_item.get("desc", ""),
        "desc": aweme_item.get("desc", ""),
        "create_time": aweme_item.get("create_time"),
        "user_id": user_info.get("uid"),
        "sec_uid": user_info.get("sec_uid"),
        "nickname": user_info.get("nickname"),
        "liked_count": str(interact.get("digg_count")),
        "collected_count": str(interact.get("collect_count")),
        "comment_count": str(interact.get("comment_count")),
        "share_count": str(interact.get("share_count")),
        "ip_location": aweme_item.get("ip_label", ""),
        "aweme_url": f"https://www.douyin.com/video/{aweme_id}",
        "cover_url": _extract_content_cover_url(aweme_item),
        "video_download_url": _extract_video_download_url(aweme_item),
        # 把原始的 music 字典也传过去，方便 store 提取 BGM 名字
        "music": aweme_item.get("music", {}),
        # 关键词 (非常重要，用于区分任务)
        "source_keyword": source_keyword_var.get(),
    }
    
    # 记录日志 (会自动写入 SQLite)
    utils.logger.info(f"💾 [分发] 准备入库: {save_item['title'][:15]}...", extra={"task_mode": "STORE", "keyword": save_item['source_keyword']})

    try:
        if save_item.get("source_keyword"):
            # 搜索任务 -> 进搜索表
            await insert_search_dy_content(save_item)
        else:
            # 监控任务 -> 进监控表
            await upsert_monitor_dy_video_daily(save_item)
    except Exception as e:
        utils.logger.error(f"❌ 入库失败: {e}", extra={"task_mode": "STORE"})

# 兼容性空函数 (保持空即可，防止报错)
async def batch_update_dy_aweme_comments(aweme_id, comments): 
    if not comments: return
    for c in comments: await update_dy_aweme_comment(aweme_id, c)

async def update_dy_aweme_comment(aweme_id, comment_item):
    # 调用你的新评论入库逻辑
    user_info = comment_item.get("user", {})
    save_item = {
        "comment_id": comment_item.get("cid"),
        "aweme_id": aweme_id,
        "content": comment_item.get("text"),
        "user_id": user_info.get("uid"),
        "sec_uid": user_info.get("sec_uid"),
        "nickname": user_info.get("nickname"),
        "like_count": str(comment_item.get("digg_count", 0)),
        "sub_comment_count": str(comment_item.get("reply_comment_total", 0)),
        "create_time": comment_item.get("create_time"),
        "parent_comment_id": comment_item.get("reply_id", "0"),
        "reply_to_user_id": str(comment_item.get("reply_to_userid") or ""),
    }
    await upsert_monitor_dy_comment(save_item)

async def update_dy_aweme_image(aweme_id, content, name):
    await DouYinImage().store_image({"aweme_id": aweme_id, "pic_content": content, "extension_file_name": name})

async def update_dy_aweme_video(aweme_id, content, name):
    await DouYinVideo().store_video({"aweme_id": aweme_id, "video_content": content, "extension_file_name": name})

async def save_creator(user_id, creator):
    # 调用你的新博主入库逻辑
    user = creator.get("user", {})
    save_item = {
        "user_id": user_id,
        "sec_uid": user.get("sec_uid"),
        "nickname": user.get("nickname"),
        "fans": user.get("max_follower_count"),
        "follows": user.get("following_count"),
        "interaction": user.get("total_favorited"),
        "videos_count": user.get("aweme_count"),
        "signature": user.get("signature"),
        "ip_location": user.get("ip_location"),
        "age": user.get("age"),
        "gender": user.get("gender"),
        "mcn_name": user.get("mcn_name"),
        "avatar": user.get("avatar_thumb", {}).get("url_list", [""])[0],
    }
    await upsert_monitor_dy_creator_daily(save_item)
# -*- coding: utf-8 -*-
# 文件路径: MediaCrawler/store/douyin/__init__.py
from typing import List, Dict
import config
from var import source_keyword_var
from tools import utils

# 【保留】为了防止报错，原作者的类定义必须保留，但在下面不调用它们
from ._store_impl import *
from .douyin_store_media import *

# 【核心】你的 SocialMonitor 专属存储逻辑
from .socialmonitor_dw_store import (
    insert_search_dy_content,
    upsert_monitor_dy_creator_daily,
    upsert_monitor_dy_video_daily,
    upsert_monitor_dy_comment,
)

class DouyinStoreFactory:
    STORES = {
        "csv": DouyinCsvStoreImplement,
        "db": DouyinDbStoreImplement,
        "postgres": DouyinDbStoreImplement,
        "json": DouyinJsonStoreImplement,
        "sqlite": DouyinSqliteStoreImplement,
        "mongodb": DouyinMongoStoreImplement,
        "excel": DouyinExcelStoreImplement,
    }

    @staticmethod
    def create_store() -> AbstractStore:
        store_class = DouyinStoreFactory.STORES.get(config.SAVE_DATA_OPTION)
        if not store_class:
            raise ValueError("Invalid save option")
        return store_class()

# ================= 辅助提取函数 (保持原样) =================

def _extract_note_image_list(aweme_detail: Dict) -> List[str]:
    images_res: List[str] = []
    images: List[Dict] = aweme_detail.get("images", [])
    if not images: return []
    for image in images:
        image_url_list = image.get("url_list", [])
        if image_url_list: images_res.append(image_url_list[-1])
    return images_res

def _extract_comment_image_list(comment_item: Dict) -> List[str]:
    images_res: List[str] = []
    image_list: List[Dict] = comment_item.get("image_list", [])
    if not image_list: return []
    for image in image_list:
        image_url_list = image.get("origin_url", {}).get("url_list", [])
        if image_url_list and len(image_url_list) > 1: images_res.append(image_url_list[1])
    return images_res

def _extract_content_cover_url(aweme_detail: Dict) -> str:
    video_item = aweme_detail.get("video", {})
    raw_cover_url_list = (video_item.get("raw_cover", {}) or video_item.get("origin_cover", {})).get("url_list", [])
    if raw_cover_url_list and len(raw_cover_url_list) > 1: return raw_cover_url_list[1]
    return ""

def _extract_video_download_url(aweme_detail: Dict) -> str:
    video_item = aweme_detail.get("video", {})
    url_list = video_item.get("play_addr", {}).get("url_list", [])
    if not url_list: return ""
    return url_list[-1]

def _extract_music_download_url(aweme_detail: Dict) -> str:
    return aweme_detail.get("music", {}).get("play_url", {}).get("uri", "")

# ================= 核心存储逻辑 (已精简) =================

async def update_douyin_aweme(aweme_item: Dict):
    """存储视频详情（只存数据库，不生成 CSV/JSON 文件）"""
    aweme_id = aweme_item.get("aweme_id")
    user_info = aweme_item.get("author", {})
    interact_info = aweme_item.get("statistics", {})
    
    save_content_item = {
        "aweme_id": aweme_id,
        "aweme_type": str(aweme_item.get("aweme_type")),
        "title": aweme_item.get("desc", ""),
        "desc": aweme_item.get("desc", ""),
        "create_time": aweme_item.get("create_time"),
        "user_id": user_info.get("uid"),
        "sec_uid": user_info.get("sec_uid"),
        "short_user_id": user_info.get("short_id"),
        "user_unique_id": user_info.get("unique_id"),
        "user_signature": user_info.get("signature"),
        "nickname": user_info.get("nickname"),
        "avatar": user_info.get("avatar_thumb", {}).get("url_list", [""])[0],
        "liked_count": str(interact_info.get("digg_count")),
        "collected_count": str(interact_info.get("collect_count")),
        "comment_count": str(interact_info.get("comment_count")),
        "share_count": str(interact_info.get("share_count")),
        "ip_location": aweme_item.get("ip_label", ""),
        "last_modify_ts": utils.get_current_timestamp(),
        "aweme_url": f"https://www.douyin.com/video/{aweme_id}",
        "cover_url": _extract_content_cover_url(aweme_item),
        "video_download_url": _extract_video_download_url(aweme_item),
        "music_download_url": _extract_music_download_url(aweme_item),
        "note_download_url": ",".join(_extract_note_image_list(aweme_item)),
        "source_keyword": source_keyword_var.get(),
    }
    
    utils.logger.info(f"[Store] 处理视频: {aweme_id} | 标题: {save_content_item.get('title')[:20]}")

    # 1. 【核心】只执行 SocialMonitor 的入库逻辑
    try:
        current_keyword = save_content_item.get("source_keyword")
        if current_keyword:
            utils.logger.info(f"🔍 [Search] 关键词: {current_keyword} -> search_dy_content")
            await insert_search_dy_content(save_content_item)
        else:
            utils.logger.info(f"📈 [Monitor] 定向监控 -> monitor_dy_video_daily")
            await upsert_monitor_dy_video_daily(save_content_item)
    except Exception as e:
        utils.logger.error(f"❌ [Store] SocialMonitor存储失败: {e}")

    # 2. 【屏蔽】原作者的通用存储 (已注释，不再生成垃圾文件)
    # await DouyinStoreFactory.create_store().store_content(content_item=save_content_item)


async def batch_update_dy_aweme_comments(aweme_id: str, comments: List[Dict]):
    """批量处理评论入口"""
    if not comments: return
    for comment_item in comments:
        await update_dy_aweme_comment(aweme_id, comment_item)


async def update_dy_aweme_comment(aweme_id: str, comment_item: Dict):
    """单条评论处理"""
    comment_aweme_id = comment_item.get("aweme_id")
    if aweme_id != comment_aweme_id:
        utils.logger.error(f"[store] 评论ID不匹配: {comment_aweme_id} != {aweme_id}")
        return

    user_info = comment_item.get("user", {})
    save_comment_item = {
        # 直接获取 cid (修复了之前的变量名 Bug)
        "comment_id": comment_item.get("cid"), 
        
        "create_time": comment_item.get("create_time"),
        "ip_location": comment_item.get("ip_label", ""),
        "aweme_id": aweme_id,
        "content": comment_item.get("text"),
        "user_id": user_info.get("uid"),
        "sec_uid": user_info.get("sec_uid"),
        "short_user_id": user_info.get("short_id"),
        "user_unique_id": user_info.get("unique_id"),
        "user_signature": user_info.get("signature"),
        "nickname": user_info.get("nickname"),
        "avatar": user_info.get("avatar_thumb", {}).get("url_list", [""])[0],
        "sub_comment_count": str(comment_item.get("reply_comment_total", 0)),
        "like_count": str(comment_item.get("digg_count", 0)),
        "last_modify_ts": utils.get_current_timestamp(),
        "parent_comment_id": comment_item.get("reply_id", "0"),
        
        # 提取被回复人ID (修复完善)
        "reply_to_user_id": str(comment_item.get("reply_to_userid") or comment_item.get("reply_comment_userid") or ""),
        
        "pictures": ",".join(_extract_comment_image_list(comment_item)),
    }
    
    # 1. 【屏蔽】原作者的 CSV/JSON 存储
    # await DouyinStoreFactory.create_store().store_comment(comment_item=save_comment_item)
    
    # 2. 【核心】存入 monitor_dy_comment 数据库
    try:
        await upsert_monitor_dy_comment(save_comment_item)
    except Exception as e:
        utils.logger.error(f"❌ [Store] 评论存储失败: {e}")


async def save_creator(user_id: str, creator: Dict):
    """存储博主信息"""
    user_info = creator.get("user", {})
    local_db_item = {
        "user_id": user_id,
        "sec_uid": user_info.get("sec_uid", ""),
        "nickname": user_info.get("nickname"),
        "follows": user_info.get("following_count", 0),
        "fans": user_info.get("max_follower_count", 0),
        "interaction": user_info.get("total_favorited", 0),
        "videos_count": user_info.get("aweme_count", 0),
        "last_modify_ts": utils.get_current_timestamp(),
    }
    utils.logger.info(f"[Store] 处理博主: {local_db_item['nickname']}")
    
    # 1. 【屏蔽】原作者的存储
    # await DouyinStoreFactory.create_store().store_creator(local_db_item)
    
    # 2. 【核心】存入 monitor_dy_creator_daily 数据库
    try:
        await upsert_monitor_dy_creator_daily(local_db_item)
    except Exception as e:
        utils.logger.error(f"❌ [Store] 博主日报存储失败: {e}")


async def update_dy_aweme_image(aweme_id, pic_content, extension_file_name):
    """图片下载逻辑 (依赖 ENABLE_GET_MEIDAS 配置)"""
    await DouYinImage().store_image({"aweme_id": aweme_id, "pic_content": pic_content, "extension_file_name": extension_file_name})

async def update_dy_aweme_video(aweme_id, video_content, extension_file_name):
    """视频下载逻辑 (依赖 ENABLE_GET_MEIDAS 配置)"""
    await DouYinVideo().store_video({"aweme_id": aweme_id, "video_content": video_content, "extension_file_name": extension_file_name})
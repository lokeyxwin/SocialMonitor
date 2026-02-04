# 文件路径: MediaCrawler/store/raw_data_store.py
import json
import datetime
from sqlalchemy import text
from database.db import get_async_engine  # 引入新修好的引擎
from tools import utils

async def save_raw_response(platform: str, url: str, data: dict):
    if not data:
        return

    try:
        api_endpoint = url.split("douyin.com")[-1].split("?")[0]
        if len(api_endpoint) > 90:
            api_endpoint = api_endpoint[:90]
    except:
        api_endpoint = "unknown"

    sql = text("""
        INSERT INTO crawler_raw_data (platform, request_url, api_endpoint, response_json, create_time)
        VALUES (:platform, :request_url, :api_endpoint, :response_json, :create_time)
    """)

    try:
        json_str = json.dumps(data, ensure_ascii=False)
        current_time = datetime.datetime.now()

        # 使用全局引擎 + begin() 事务上下文
        engine = get_async_engine()
        async with engine.begin() as conn:
            await conn.execute(sql, {
                "platform": platform,
                "request_url": url,
                "api_endpoint": api_endpoint,
                "response_json": json_str,
                "create_time": current_time
            })
            
    except Exception as e:
        utils.logger.error(f"❌ [RawData] 数据保存失败: {e}")
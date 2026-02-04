# 文件路径: MediaCrawler/database/db.py
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from config import db_config

# 全局单例引擎
AsyncEngine = None

def get_async_engine():
    global AsyncEngine
    if AsyncEngine is not None:
        return AsyncEngine
    
    # 构造连接字符串
    DB_URL = (
        f"mysql+aiomysql://{db_config.MYSQL_DB_USER}:{db_config.MYSQL_DB_PWD}"
        f"@{db_config.MYSQL_DB_HOST}:{db_config.MYSQL_DB_PORT}/{db_config.MYSQL_DB_NAME}"
        f"?charset=utf8mb4"
    )
    
    # 创建引擎 (连接池配置)
    AsyncEngine = create_async_engine(
        DB_URL, 
        echo=False, 
        pool_size=20,       # 保持20个连接
        pool_recycle=3600   # 1小时回收
    )
    return AsyncEngine

async def close():
    global AsyncEngine
    if AsyncEngine:
        await AsyncEngine.dispose()

async def init_db(db_type: str = None):
    from database.db_session import create_tables
    await create_tables(db_type)
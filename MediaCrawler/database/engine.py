# 文件路径: MediaCrawler/database/engine.py
from sqlalchemy.ext.asyncio import create_async_engine
from config import db_config

def get_async_engine():
    """
    独立的数据库引擎获取函数，避免循环引用
    """
    DB_URL = (
        f"mysql+aiomysql://{db_config.MYSQL_DB_USER}:{db_config.MYSQL_DB_PWD}"
        f"@{db_config.MYSQL_DB_HOST}:{db_config.MYSQL_DB_PORT}/{db_config.MYSQL_DB_NAME}"
        f"?charset=utf8mb4"
    )
    # echo=False 不打印刷屏的 SQL 日志
    return create_async_engine(DB_URL, echo=False)
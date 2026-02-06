# -*- coding: utf-8 -*-
# 文件路径: MediaCrawler/tools/sqlite_logger.py
import logging
import sqlite3
import datetime
import os
from queue import Queue
from threading import Thread

class SQLiteHandler(logging.Handler):
    """
    轻量级 SQLite 日志处理器 (异步写入版)
    防止日志写入卡死爬虫主进程
    """
    def __init__(self, db_path="crawler_log.db"):
        logging.Handler.__init__(self)
        self.db_path = db_path
        self.queue = Queue()
        self._init_db()
        
        # 启动一个后台线程专门写日志，不拖慢爬虫
        self.worker = Thread(target=self._worker_loop, daemon=True)
        self.worker.start()

    def _init_db(self):
        """初始化日志数据库表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crawler_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    create_time TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    task_mode TEXT,
                    keyword TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass

    def emit(self, record):
        """把日志扔进队列就走，绝不等待"""
        try:
            self.queue.put(record)
        except Exception:
            self.handleError(record)

    def _worker_loop(self):
        """后台默默写日志的工人"""
        while True:
            try:
                record = self.queue.get()
                self._write_to_db(record)
                self.queue.task_done()
            except Exception:
                pass

    def _write_to_db(self, record):
        try:
            # 提取 extra 里的字段，如果没有就是空
            task_mode = getattr(record, 'task_mode', '')
            keyword = getattr(record, 'keyword', '')
            msg = self.format(record)
            
            # 每次写入都单独连一次，避免长连接锁死
            conn = sqlite3.connect(self.db_path, timeout=5)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO crawler_logs (create_time, level, message, task_mode, keyword) VALUES (?, ?, ?, ?, ?)",
                (datetime.datetime.now(), record.levelname, msg, task_mode, keyword)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
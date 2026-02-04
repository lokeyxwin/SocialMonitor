from enum import Enum
from typing import Optional, Literal
from pydantic import BaseModel


class PlatformEnum(str, Enum):
    """Supported media platforms"""
    XHS = "xhs"
    DOUYIN = "dy"
    KUAISHOU = "ks"
    BILIBILI = "bili"
    WEIBO = "wb"
    TIEBA = "tieba"
    ZHIHU = "zhihu"


class LoginTypeEnum(str, Enum):
    """Login method"""
    QRCODE = "qrcode"
    PHONE = "phone"
    COOKIE = "cookie"


class CrawlerTypeEnum(str, Enum):
    """Crawler type"""
    SEARCH = "search"
    DETAIL = "detail"
    CREATOR = "creator"


class SaveDataOptionEnum(str, Enum):
    """Data save option"""
    CSV = "csv"
    DB = "db"
    JSON = "json"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    EXCEL = "excel"


class CrawlerStartRequest(BaseModel):
    """Crawler start request"""
    platform: PlatformEnum
    login_type: LoginTypeEnum = LoginTypeEnum.QRCODE
    crawler_type: CrawlerTypeEnum = CrawlerTypeEnum.SEARCH
    keywords: str = ""  # Keywords for search mode
    specified_ids: str = ""  # Post/video ID list for detail mode, comma-separated
    creator_ids: str = ""  # Creator ID list for creator mode, comma-separated
    start_page: int = 1
    enable_comments: bool = True
    enable_sub_comments: bool = False
    save_option: SaveDataOptionEnum = SaveDataOptionEnum.JSON
    cookies: str = ""
    headless: bool = False


class CrawlerStatusResponse(BaseModel):
    """Crawler status response"""
    status: Literal["idle", "running", "stopping", "error"]
    platform: Optional[str] = None
    crawler_type: Optional[str] = None
    started_at: Optional[str] = None
    error_message: Optional[str] = None


class LogEntry(BaseModel):
    """Log entry"""
    id: int
    timestamp: str
    level: Literal["info", "warning", "error", "success", "debug"]
    message: str


class DataFileInfo(BaseModel):
    """Data file information"""
    name: str
    path: str
    size: int
    modified_at: str
    record_count: Optional[int] = None

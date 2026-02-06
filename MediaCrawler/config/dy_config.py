# 抖音平台配置
PUBLISH_TIME_TYPE = 0
# ==================== 抖音搜索排序配置 ====================
# 搜索排序模式
# 0: 综合排序 (默认)
# 1: 最热/点赞最多 (Popular)
# 2: 最新发布 (Latest)
DY_SEARCH_SORT_TYPE = 0


# 指定DY视频URL列表 (支持多种格式)
# 支持格式:
# 1. 完整视频URL: "https://www.douyin.com/video/7525538910311632128"
# 2. 带modal_id的URL: "https://www.douyin.com/user/xxx?modal_id=7525538910311632128"
# 3. 搜索页带modal_id: "https://www.douyin.com/root/search/python?modal_id=7525538910311632128"
# 4. 短链接: "https://v.douyin.com/drIPtQ_WPWY/"
# 5. 纯视频ID: "7280854932641664319"
DY_SPECIFIED_ID_LIST = [
    "https://www.douyin.com/video/7525538910311632128",
    "https://v.douyin.com/drIPtQ_WPWY/",
    "https://www.douyin.com/user/MS4wLjABAAAATJPY7LAlaa5X-c8uNdWkvz0jUGgpw4eeXIwu_8BhvqE?from_tab_name=main&modal_id=7525538910311632128",
    "7202432992642387233",
    # ........................
]

# 指定DY创作者URL列表 (支持完整URL或sec_user_id)
# 支持格式:
# 1. 完整创作者主页URL: "https://www.douyin.com/user/MS4wLjABAAAATJPY7LAlaa5X-c8uNdWkvz0jUGgpw4eeXIwu_8BhvqE?from_tab_name=main"
# 2. sec_user_id: "MS4wLjABAAAATJPY7LAlaa5X-c8uNdWkvz0jUGgpw4eeXIwu_8BhvqE"
DY_CREATOR_ID_LIST = [
    "https://www.douyin.com/user/MS4wLjABAAAAHrDUdR2RQUKB2ELVAmES-xXs4gQ_qtkNxSbWartbEnA?from_tab_name=main",
    "MS4wLjABAAAAHrDUdR2RQUKB2ELVAmES-xXs4gQ_qtkNxSbWartbEnA"
    # ........................
]

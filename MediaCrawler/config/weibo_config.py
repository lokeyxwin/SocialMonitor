# 微博平台配置

# 搜索类型，具体的枚举值在media_platform/weibo/field.py中
WEIBO_SEARCH_TYPE = "default"

# 指定微博ID列表
WEIBO_SPECIFIED_ID_LIST = [
    "4982041758140155",
    # ........................
]

# 指定微博用户ID列表
WEIBO_CREATOR_ID_LIST = [
    "5756404150",
    # ........................
]

# 是否开启微博爬取全文的功能，默认开启
# 如果开启的话会增加被风控的概率，相当于一个关键词搜索请求会再遍历所有帖子的时候，再请求一次帖子详情
ENABLE_WEIBO_FULL_TEXT = True

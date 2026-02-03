import streamlit as st
import pandas as pd
# 假设这是你的爬虫函数
from social_monitor.crawler.core import search_xhs_keyword


@st.dialog("全网搜索结果预览", width="large")
def show_search_results(keyword):
    st.caption(f"正在实时抓取 '{keyword}' 的相关数据，请稍候...")

    # 1. 调用爬虫 (这里会卡住几秒，所以需要 spinner)
    with st.spinner("正在从新红书/抖音打捞数据..."):
        # 爬虫返回一个大字典，包含 'users' 和 'notes' 两个列表
        # data = search_xhs_keyword(keyword)
        # 模拟数据
        data = {
            'users': [{'name': '秒懂金融', 'followers': '65.5w', 'id': 'pacinging', 'avatar': '👤'}],
            'notes': [{'title': '垃圾分类为什么没人提了？', 'likes': '4.9w', 'date': '2026-01-27'}]
        }

    # 2. 布局：利用 Columns 分栏复刻新红的界面
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("👤 相关账号")
        # 遍历展示前 5 个账号
        for user in data.get('users', [])[:5]:
            with st.container(border=True):
                c1, c2 = st.columns([1, 3])
                c1.write(user['avatar'])  # 实际用 st.image
                c2.markdown(f"**{user['name']}**")
                c2.caption(f"粉丝: {user['followers']} | ID: {user['id']}")
                if c2.button("监控它", key=f"btn_{user['id']}"):
                    st.toast(f"已将 {user['name']} 加入监控池")

    with col2:
        st.subheader("📝 相关笔记")
        for note in data.get('notes', [])[:5]:
            with st.container(border=True):
                st.write(note['title'])
                st.caption(f"点赞: {note['likes']} | 时间: {note['date']}")


# --- 主界面 ---
st.title("舆情雷达搜索")
keyword = st.text_input("输入关键词（如：细胞存储）", placeholder="回车开始全网检索...")

if keyword:
    if st.button("开始挖掘"):
        show_search_results(keyword)
# social_monitor/web/views/management.py
import streamlit as st
from streamlit_option_menu import option_menu
# 引用我们做好的卡片组件
from social_monitor.web.components.account_card import render_account_card

def render():
    st.title("👥 监控对象管理")

    # 1. 顶部工具栏 (模拟 CRM 的操作区)
    col_tools1, col_tools2 = st.columns([3, 1])
    with col_tools1:
        # 使用 Pills (胶囊按钮) 做筛选 (Streamlit 1.34+ 特性，如果报错换成 radio)
        filter_status = st.radio(
            "状态筛选",
            ["全部", "🟢 运行中", "🔴 异常/断更"],
            horizontal=True,
            label_visibility="collapsed"
        )
    with col_tools2:
        if st.button("➕ 新增监控", type="primary", use_container_width=True):
            st.toast("点击了新增按钮")

    st.markdown("---")

    # 2. 模拟数据库数据 (Mock Data)
    # 等会儿我们会写 database/crud.py 来替换掉这里
    mock_data = [
        {
            "id": "user_001",
            "name": "丁香医生",
            "avatar": "https://p1-1251933758.cos.ap-shanghai.myqcloud.com/avatar_mock_1.jpg", # 找个能访问的图
            "fans": "502.1w",
            "fans_delta": "+2300",
            "last_active": "昨天 18:00",
            "hot_count": "152",
            "desc": "专注医疗科普...",
            "status": "active",
            "tags": [{"text": "头部大V", "color": "blue"}, {"text": "科普", "color": "green"}]
        },
        {
            "id": "user_002",
            "name": "某某干细胞中介",
            "avatar": "https://ui-avatars.com/api/?name=Scam&background=ff0000&color=fff",
            "fans": "120",
            "fans_delta": "0",
            "last_active": "30天前",
            "hot_count": "0",
            "desc": "高价回收...",
            "status": "error",
            "tags": [{"text": "竞品", "color": "red"}, {"text": "疑似断更", "color": "gray"}]
        }
    ]

    # 3. 根据筛选逻辑过滤数据
    display_list = mock_data
    if "运行中" in filter_status:
        display_list = [x for x in mock_data if x['status'] == 'active']
    elif "异常" in filter_status:
        display_list = [x for x in mock_data if x['status'] == 'error']

    # 4. 渲染列表
    if not display_list:
        st.info("当前分类下没有账号")
    else:
        for account in display_list:
            render_account_card(account)
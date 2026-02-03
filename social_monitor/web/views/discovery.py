# social_monitor/web/views/discovery.py
import streamlit as st


def render():
    # --- 这里就是右侧的画布，你想怎么布局都行 ---

    st.title("🔍 全网账号雷达")

    # 比如你想把搜索框和按钮分开放
    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_input("搜点什么...", key="keyword")
    with col2:
        st.button("搜索")

    st.write("下面放表格...")
    # ... 你的其他布局代码
#!/bin/bash

# 定义项目根目录名称
PROJECT_ROOT="05_socialmonitor"

echo "📂 开始构建项目结构: $PROJECT_ROOT ..."

# 1. 创建根目录
mkdir -p "$PROJECT_ROOT"
cd "$PROJECT_ROOT" || exit



# ==========================================
# 3. 创建 Backend (FastAPI) 结构
# ==========================================
echo "   ├── 创建 Backend (FastAPI) 结构..."
mkdir -p backend/app/api/endpoints
mkdir -p backend/app/core
mkdir -p backend/app/models
mkdir -p backend/app/schemas
mkdir -p backend/app/services

# 创建后端文件
touch backend/app/api/endpoints/monitor.py
touch backend/app/api/endpoints/analysis.py
touch backend/app/api/endpoints/reports.py
touch backend/app/api/endpoints/__init__.py # Python包需要

touch backend/app/api/api.py
touch backend/app/api/__init__.py

touch backend/app/core/config.py
touch backend/app/core/database.py
touch backend/app/core/__init__.py

touch backend/app/models/keyword.py
touch backend/app/models/sentiment.py
touch backend/app/models/__init__.py

touch backend/app/schemas/task.py
touch backend/app/schemas/chart.py
touch backend/app/schemas/__init__.py

touch backend/app/services/crawler_runner.py
touch backend/app/services/data_cleaner.py
touch backend/app/services/nlp_engine.py
touch backend/app/services/__init__.py

touch backend/app/main.py
touch backend/app/__init__.py

touch backend/requirements.txt
touch backend/.env

# ==========================================
# 4. 创建 Frontend (Vue3) 结构
# ==========================================
echo "   ├── 创建 Frontend (Vue3) 结构..."
mkdir -p frontend/public
mkdir -p frontend/src/api
mkdir -p frontend/src/assets
mkdir -p frontend/src/components/Charts
mkdir -p frontend/src/components/DataTable
mkdir -p frontend/src/views
mkdir -p frontend/src/router
mkdir -p frontend/src/store

# 创建前端文件
touch frontend/src/api/monitor.js
touch frontend/src/api/chart.js

touch frontend/src/views/Dashboard.vue
touch frontend/src/views/TaskManager.vue
touch frontend/src/views/DataDetail.vue

touch frontend/src/App.vue
touch frontend/src/main.js

touch frontend/package.json
touch frontend/vite.config.js

# ==========================================
# 5. 创建 Database 结构
# ==========================================
echo "   ├── 创建 Database 目录..."
mkdir -p database/migrations
touch database/init.sql

# ==========================================
# 6. 创建 Logs 结构
# ==========================================
echo "   ├── 创建 Logs 目录..."
mkdir -p logs/crawler
mkdir -p logs/backend
# 创建个占位文件，防止空文件夹被git忽略
touch logs/crawler/.gitkeep
touch logs/backend/.gitkeep

echo "✅ 项目结构生成完毕！位置: $(pwd)"
echo "💡 提示: 请确保将 MediaCrawler 的实际代码放入 '05_socialmonitor/MediaCrawler' 目录中。"
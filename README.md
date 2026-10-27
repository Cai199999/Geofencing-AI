## 🏢 园区地理围栏与 AI 智能管家系统 (Geofencing & AI Agent)

这是一个基于 **微服务架构** 的全栈实战项目。系统实现了对园区内人员与车辆的实时定位与地理围栏（Geofencing）判定，并接入了 **DeepSeek 大模型**，实现了自然语言的智能交互与数据播报。

## ✨ 核心功能

- **实时地图可视化**：使用百度地图 API，绘制园区大围栏（蓝色）与楼栋小围栏（红色），并实时展示目标的移动轨迹。
- **空间几何判定**：后端使用 `Shapely` 库，高效计算人员/车辆的坐标（Point）是否在围栏（Polygon）内部。
- **数据持久化**：使用 `SQLite` 数据库，自动记录每一次“进入/离开”的报警事件日志。
- **AI 智能管家**：前端悬浮聊天框，用户可输入自然语言（如：“user_001 离开过几次？”），AI 会结合数据库统计结果给出回答。
- **安全隔离**：隐藏了真实的 API Key，使用 `.env` 环境变量进行管理。

---

## 🏗️ 系统架构

本项目采用前后端分离 + 多语言网关的微服务架构：

1. **前端 (Frontend)**：HTML + JavaScript + 百度地图 BMap API。
2. **Java 业务网关 (Java Backend)**：Spring Boot 8080 端口，负责处理跨域请求，将前端的聊天请求安全地转发给底层 AI 引擎。
3. **Python 核心引擎 (Python Backend)**：Flask 5000 端口，负责地理围栏的复杂数学计算、数据库读写，以及调用 DeepSeek 大模型。

**数据流向**：`浏览器前端` ➡️ `Java Gateway (8080)` ➡️ `Python Engine (5000)` ➡️ `DeepSeek API`

---

## 🚀 本地运行指南

### 1. 环境要求
- Python 3.8+
- Java 17+ (及 Maven)
- 一个百度地图开放平台的浏览器端 AK
- 一个 DeepSeek 的 API Key

### 2. 克隆项目并进入根目录
```bash
git clone https://github.com/Cai199999/Geofencing-AI.git
cd Geofencing-AI
3. 配置前端（百度地图 AK）
打开 templates/index.html 文件，找到加载百度地图的 <script> 标签，将 YOUR_BAIDU_AK 替换为你自己申请的浏览器端 AK：

html
<!-- 替换前 -->
<script type="text/javascript" src="https://api.map.baidu.com/api?v=3.0&ak=YOUR_BAIDU_AK"></script>
4. 配置后端（DeepSeek API Key）
在项目根目录下，新建一个名为 .env 的文件，填入你的 DeepSeek Key：

text
DEEPSEEK_API_KEY=sk-你的真实DeepSeekKey
5. 启动 Python 核心引擎
bash
# 安装依赖 (Ubuntu/Debian 环境)
sudo apt install python3-flask python3-shapely python3-openai python3-dotenv

# 启动服务
python3 demo.py
6. 启动 Java 网关 (新开一个终端)
bash
# 进入 Java 项目目录
cd agent-demo

# 启动服务
mvn spring-boot:run
7. 前端访问
在浏览器中打开 http://127.0.0.1:5000。
## 🖼️ 界面演示
<img width="400" height="281" alt="db7e5adde5c2ef8333f72e81e934dd6d_raw" src="https://github.com/user-attachments/assets/4b1c103c-d6f2-4634-b62f-605e517d9dfc" />

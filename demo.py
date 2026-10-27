# demo.py
from flask import Flask, jsonify, render_template
from shapely.geometry import Point, Polygon
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import sqlite3
import os
import random

app = Flask(__name__)
# ==========================================
# 数据库操作模块
# ==========================================
DB_FILE = 'geofence.db'

def init_db():
    """初始化数据库，创建表"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            event_type TEXT,
            fence_name TEXT,
            event_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_event_to_db(device_id, event_type, fence_name):
    """将进出事件写入数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO event_logs (device_id, event_type, fence_name, event_time) VALUES (?, ?, ?, ?)",
        (device_id, event_type, fence_name, now)
    )
    conn.commit()
    conn.close()

# 启动时初始化一次数据库
init_db()
# ==========================================
# 1. 定义【启明国际B座】小围栏 (红色矩形 - 保持不变)
# ==========================================
BUILDING_BOUNDARY_COORDS = [
    (116.480995, 40.018371),  # 西南角
    (116.481798, 40.018380),  # 东南角
    (116.481816, 40.018652),  # 东北角
    (116.480983, 40.018641)  # 西北角
]
building_polygon = Polygon(BUILDING_BOUNDARY_COORDS)

# ==========================================
# 2. 定义【望京科技园】大围栏 (蓝色矩形 - 已更新为你提供的最新坐标)
# 逆时针顺序: 西南 -> 东南 -> 东北 -> 西北
# ==========================================
PARK_BOUNDARY_COORDS = [
    (116.479806, 40.017559),  # 西南角 (原第4点)
    (116.482108, 40.017642),  # 东南角 (原第3点)
    (116.481958, 40.019861),  # 东北角 (原第2点)
    (116.479706, 40.019804)  # 西北角 (原第1点)
]
park_polygon = Polygon(PARK_BOUNDARY_COORDS)

# 状态记录
tracking_state = {
    "user_001": {"type": "人员", "in_park": False, "in_building": False},
    "car_京A88888": {"type": "车辆", "in_park": False, "in_building": False}
}

# 计算中心点
b_center_lon = (116.480995 + 116.481816) / 2
b_center_lat = (40.018371 + 40.018652) / 2

# 重新计算大围栏的中心点
park_center_lon = (116.479806 + 116.482108 + 116.481958 + 116.479706) / 4
park_center_lat = (40.017559 + 40.017642 + 40.019861 + 40.019804) / 4


# 模拟生成坐标
def generate_point(device_type):
    if device_type == "人员":
        # 人员在 B 座中心附近徘徊（范围稍微大一点，确保能跨出红框，测试进出）
        lon = round(b_center_lon + random.uniform(-0.0012, 0.0012), 6)
        lat = round(b_center_lat + random.uniform(-0.0006, 0.0006), 6)
    else:
        # 车辆在整个望京科技园大蓝框内徘徊
        lon = round(park_center_lon + random.uniform(-0.004, 0.004), 6)
        lat = round(park_center_lat + random.uniform(-0.004, 0.004), 6)
    return lon, lat


@app.route('/')
def index():
    return render_template('index.html',
                           park_boundary=PARK_BOUNDARY_COORDS,
                           building_boundary=BUILDING_BOUNDARY_COORDS,
                           center=[park_center_lon, park_center_lat])


@app.route('/api/get_locations')
def get_locations():
    logs = []
    response_data = {}

    for dev_id, info in tracking_state.items():
        lon, lat = generate_point(info["type"])
        point = Point(lon, lat)

        # --- 判定逻辑 1：是否在望京科技园 (蓝框) ---
        in_park_now = park_polygon.contains(point)
        if in_park_now and not info["in_park"]:
            logs.append(f"🚨 {info['type']} {dev_id} 进入望京科技园")
            log_event_to_db(dev_id, "进入", "望京科技园") 
        elif not in_park_now and info["in_park"]:
            logs.append(f"🚨 {info['type']} {dev_id} 离开望京科技园")
            log_event_to_db(dev_id, "离开", "望京科技园")  
        info["in_park"] = in_park_now

        # --- 判定逻辑 2：是否在启明B座 (红框) ---
        if info["type"] == "人员":
            in_building_now = building_polygon.contains(point)
            if in_building_now and not info["in_building"]:
                logs.append(f"🏢 员工 {dev_id} 进入 启明B座")
                log_event_to_db(dev_id, "进入", "启明B座")  
            elif not in_building_now and info["in_building"]:
                logs.append(f"🚶 员工 {dev_id} 离开 启明B座")
                log_event_to_db(dev_id, "离开", "启明B座")
            info["in_building"] = in_building_now
        else:
            in_building_now = False

        status = "园区外"
        if in_park_now: status = "园区内"
        if in_building_now: status = "B座内"

        response_data[dev_id] = {
            "lon": lon,
            "lat": lat,
            "status": status,
            "type": info["type"]
        }

    return jsonify({"data": response_data, "logs": logs})
# 初始化 DeepSeek 客户端
# 从环境变量读取 Key
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")

if not DEEPSEEK_KEY:
    print("⚠️ 警告: 未检测到环境变量 DEEPSEEK_API_KEY，AI 聊天功能将不可用。")

ai_client = OpenAI(
    api_key=DEEPSEEK_KEY, 
    base_url="https://api.deepseek.com"
)

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    from flask import request
    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"reply": "请告诉我你需要什么帮助？"})
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

     # 查询人员离开望京科技园的次数
    cursor.execute("SELECT COUNT(*) FROM event_logs WHERE device_id='user_001' AND event_type='离开' AND fence_name='望京科技园'")
    leave_count = cursor.fetchone()[0]
    
    # 查询当前的日志数量（作为活跃度参考）
    cursor.execute("SELECT COUNT(*) FROM event_logs")
    total_events = cursor.fetchone()[0]
    
    conn.close()

    # 把查询到的真实数据拼接到 Prompt 里
    current_status = f"数据库统计信息：人员 user_001 累计离开望京科技园 {leave_count} 次；系统总计记录了 {total_events} 条进出事件。"
    
    try:
        response = ai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"你是望京科技园区的智能管家。{current_status}。请用简短、专业的语气回答管理员的问题。"},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"AI 引擎连接失败: {str(e)}"})

if __name__ == '__main__':
    print(f"🚀 系统启动！望京科技园中心点: {park_center_lon:.6f}, {park_center_lat:.6f}")
    app.run(debug=True, port=5000)

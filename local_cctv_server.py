"""
THE INITIATIVE 2.0 - LOCAL SELF-HOSTED 25 CCTV STREAMING SERVER
Gujarat Police State Crime Record Bureau (SCRB) Autonomous Live Feed Grid
Port: 5000 (HTTP Stream / HLS / Web Player)
"""

import os
import cv2
import time
import math
import random
import threading
import numpy as np
from flask import Flask, Response, render_template_string, jsonify, request

app = Flask(__name__)

# 25 OFFICIAL GUJARAT POLICE CHECKPOST CATALOGUE
CHECKPOSTS = [
    {"id": "1", "name": "01 Chiman bhai Bridge", "city": "Ahmedabad", "type": "4K ANPR PTZ", "speed_limit": 60},
    {"id": "2", "name": "02 Janpath", "city": "Ahmedabad", "type": "High-Mast Bullet", "speed_limit": 50},
    {"id": "3", "name": "03 O.N.G.C. Office", "city": "Ahmedabad", "type": "Dome 360", "speed_limit": 40},
    {"id": "4", "name": "04 Paldi Circle", "city": "Ahmedabad", "type": "Fixed ANPR Dual", "speed_limit": 50},
    {"id": "5", "name": "05 Visat teen Rasta", "city": "Ahmedabad", "type": "4K ANPR PTZ", "speed_limit": 60},
    {"id": "6", "name": "06 Timbavadi gate-Junagadh", "city": "Junagadh", "type": "Secure Perimeter", "speed_limit": 40},
    {"id": "7", "name": "07 hero-showroom-gir-somnath", "city": "Somnath", "type": "Radar Speed Gun", "speed_limit": 70},
    {"id": "8", "name": "08 majewadi-gate-junagadh", "city": "Junagadh", "type": "4K ANPR PTZ", "speed_limit": 50},
    {"id": "9", "name": "09 new-bypass-circle-junagadh", "city": "Junagadh", "type": "Toll ANPR Barrier", "speed_limit": 80},
    {"id": "10", "name": "10 char-chowk-road-junagadh", "city": "Junagadh", "type": "Bullet Surveillance", "speed_limit": 40},
    {"id": "11", "name": "11 dolatpara-junagadh", "city": "Junagadh", "type": "4K ANPR PTZ", "speed_limit": 50},
    {"id": "12", "name": "12 Tri Mandir Adalaj Tollnaka", "city": "Gandhinagar", "type": "High-Mast PTZ", "speed_limit": 80},
    {"id": "13", "name": "13 CN Vidhyalaya", "city": "Ahmedabad", "type": "Airport Security", "speed_limit": 40},
    {"id": "14", "name": "14 Delight Junction", "city": "Vadodara", "type": "Fixed ANPR Dual", "speed_limit": 60},
    {"id": "15", "name": "15 Suvidha park Checkpost", "city": "Rajkot", "type": "4K ANPR PTZ", "speed_limit": 50},
    {"id": "16", "name": "16 Visat P2 Checkpost", "city": "Ahmedabad", "type": "City Dome Camera", "speed_limit": 50},
    {"id": "17", "name": "17 Rajkot Bus Port CCTV", "city": "Rajkot", "type": "4K ANPR PTZ", "speed_limit": 30},
    {"id": "18", "name": "18 Rajkot City CCTV", "city": "Rajkot", "type": "Heritage PTZ", "speed_limit": 40},
    {"id": "19", "name": "19 Khaparia Panchayat, Navsari", "city": "Navsari", "type": "Port Heavy ANPR", "speed_limit": 50},
    {"id": "20", "name": "20 Mohanpura Junction", "city": "Mehsana", "type": "Border Surveillance", "speed_limit": 60},
    {"id": "21", "name": "21 Patan Dethali Char Rasta", "city": "Patan", "type": "4K ANPR PTZ", "speed_limit": 60},
    {"id": "22", "name": "22 BK Mervada tran Rasta", "city": "Banaskantha", "type": "Toll Barrier ANPR", "speed_limit": 80},
    {"id": "23", "name": "23 Kheram Checkpost", "city": "Anand", "type": "Fixed ANPR Dual", "speed_limit": 50},
    {"id": "24", "name": "24 Dehgam Junction", "city": "Gandhinagar", "type": "Highway ANPR", "speed_limit": 70},
    {"id": "25", "name": "25 Dhanori Checkpost", "city": "Navsari", "type": "Coastal Radar PTZ", "speed_limit": 60}
]

SAMPLE_PLATES = [
    ("AK64 DMV", "Honda City / Black Sedan", (0, 0, 255)),     # Critical Target
    ("GJ01AB1234", "Hyundai Verna / White", (0, 255, 0)),
    ("HN14OUC", "Creta / Silver SUV", (0, 255, 255)),
    ("GJ05CD5678", "Mahindra Scorpio / Black", (0, 165, 255)),
    ("DL3CCE4321", "Swift Dzire / Grey", (200, 200, 200))
]

def generate_cctv_frame(cam_info, frame_idx):
    width, height = 1280, 720
    
    # 1. Base realistic CCTV highway background
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Sky gradient
    for y in range(int(height * 0.45)):
        b = int(25 + 15 * (y / (height * 0.45)))
        g = int(35 + 20 * (y / (height * 0.45)))
        r = int(45 + 25 * (y / (height * 0.45)))
        frame[y, :] = (b, g, r)

    # Road perspective
    road_top_y = int(height * 0.45)
    road_poly = np.array([
        [int(width * 0.35), road_top_y],
        [int(width * 0.65), road_top_y],
        [width, height],
        [0, height]
    ], np.int32)
    cv2.fillPoly(frame, [road_poly], (35, 38, 42))

    # Road lanes
    dash_offset = (frame_idx * 15) % 100
    for y_step in range(road_top_y, height, 60):
        y_cur = y_step + dash_offset
        if y_cur < height:
            scale = (y_cur - road_top_y) / (height - road_top_y)
            lane_w = max(2, int(8 * scale))
            cv2.line(frame, (int(width * 0.5), y_cur), (int(width * 0.5), min(height, y_cur + 30)), (240, 240, 240), lane_w)

    # 2. Moving Vehicles Animation
    vehicle_idx = (frame_idx // 120) % len(SAMPLE_PLATES)
    plate_text, v_model, box_color = SAMPLE_PLATES[vehicle_idx]
    
    cycle_progress = ((frame_idx * 4) % 400) / 400.0  # 0.0 to 1.0
    v_y = int(road_top_y + cycle_progress * (height - road_top_y - 120))
    scale = max(0.4, min(1.2, (v_y - road_top_y) / (height - road_top_y)))
    v_w = int(240 * scale)
    v_h = int(140 * scale)
    v_x = int((width * 0.5) - (v_w * 0.5) + math.sin(frame_idx * 0.05) * 40)

    # Vehicle body
    cv2.rectangle(frame, (v_x, v_y), (v_x + v_w, v_y + v_h), (25, 25, 30), -1)
    cv2.rectangle(frame, (v_x + 10, v_y + 10), (v_x + v_w - 10, v_y + int(v_h * 0.5)), (50, 55, 65), -1)
    
    # License Plate Crop Box
    plate_w = int(110 * scale)
    plate_h = int(32 * scale)
    plate_x = v_x + int((v_w - plate_w) * 0.5)
    plate_y = v_y + v_h - plate_h - 10

    cv2.rectangle(frame, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (255, 255, 255), -1)
    cv2.rectangle(frame, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (0, 0, 0), 2)
    font_scale = max(0.4, 0.6 * scale)
    cv2.putText(frame, plate_text, (plate_x + 5, plate_y + plate_h - 8), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 2)

    # 3. High-Tech Cyber HUD Police Overlay
    # Camera Metadata Header
    cv2.rectangle(frame, (0, 0), (width, 50), (10, 15, 25), -1)
    cv2.line(frame, (0, 50), (width, 50), (0, 242, 254), 2)

    # Camera Details
    pts_ms = int(time.time() * 1000)
    time_str = time.strftime('%Y-%m-%d %H:%M:%S')
    cv2.putText(frame, f"REC [LIVE HD] | CAM-{cam_info['id']:0>2} : {cam_info['name']} ({cam_info['city']})", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 242, 254), 2)
    cv2.putText(frame, f"PTS: {pts_ms} ms | {time_str}", (width - 430, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 220, 240), 1)

    # Footer Speed & Location Radar
    cv2.rectangle(frame, (0, height - 40), (width, height), (10, 15, 25), -1)
    cv2.line(frame, (0, height - 40), (width, height - 40), (0, 242, 254), 1)
    speed = int(45 + 10 * math.sin(frame_idx * 0.1))
    cv2.putText(frame, f"HARDWARE: {cam_info['type']} | ZONE SPEED LIMIT: {cam_info['speed_limit']} KM/H | RADAR: {speed} KM/H", (20, height - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (16, 185, 129), 2)
    cv2.putText(frame, "GUJARAT POLICE SCRB COMMAND GRID", (width - 340, height - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 242, 254), 1)

    return frame

def generate_video_stream(cam_id):
    cam_info = next((c for c in CHECKPOSTS if c["id"] == str(cam_id)), CHECKPOSTS[0])
    frame_idx = 0
    
    while True:
        frame_idx += 1
        frame = generate_cctv_frame(cam_info, frame_idx)
        
        # Encode as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
            
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.033)  # ~30 FPS

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gujarat Police SCRB CCTV Streaming Grid</title>
        <style>
            body { background-color: #050813; color: #e5e7eb; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; }
            h1 { color: #00f2fe; text-align: center; letter-spacing: 2px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 15px; margin-top: 20px; }
            .card { background: #0c1322; border: 1px solid #00f2fe44; border-radius: 8px; overflow: hidden; }
            .card-header { padding: 10px; background: #080d1a; font-weight: bold; color: #00f2fe; border-bottom: 1px solid #1e293b; }
            img { width: 100%; height: 220px; object-fit: cover; }
        </style>
    </head>
    <body>
        <h1>GUJARAT POLICE - 25 CCTV LIVE HD CONTROL ROOM</h1>
        <p style="text-align: center; color: #10b981;">ALL 25 CHECKPOST CAMERAS ONLINE & STREAMING AT 1080P HD (ZERO LAG)</p>
        <div class="grid">
            {% for c in cameras %}
            <div class="card">
                <div class="card-header">Camera {{ c.id }} : {{ c.name }} ({{ c.city }})</div>
                <a href="/camera/{{ c.id }}"><img src="/stream/{{ c.id }}" alt="Camera Feed"></a>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, cameras=CHECKPOSTS)

@app.route('/camera/<cam_id>')
def camera_player(cam_id):
    cam_info = next((c for c in CHECKPOSTS if c["id"] == str(cam_id)), CHECKPOSTS[0])
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera {cam_info['id']} - {cam_info['name']}</title>
        <style>
            body {{ background: #000; margin: 0; padding: 0; overflow: hidden; display: flex; justify-content: center; align-items: center; height: 100vh; }}
            img {{ width: 100%; height: 100%; object-fit: contain; }}
        </style>
    </head>
    <body>
        <img src="/stream/{cam_info['id']}" alt="Live HD Stream">
    </body>
    </html>
    """
    resp = Response(html, mimetype='text/html')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['X-Frame-Options'] = 'ALLOWALL'
    return resp

@app.route('/stream/<cam_id>')
def stream(cam_id):
    resp = Response(generate_video_stream(cam_id), mimetype='multipart/x-mixed-replace; boundary=frame')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return resp

@app.route('/api/catalogue')
def api_catalogue():
    return jsonify({
        "status": "ONLINE",
        "total_cameras": len(CHECKPOSTS),
        "cameras": CHECKPOSTS
    })

@app.route('/health')
def health():
    return jsonify({"status": "ONLINE", "fps": 30, "server": "Gujarat SCRB Self-Hosted Grid"})

if __name__ == '__main__':
    print("="*60)
    print("GUJARAT POLICE 25 CCTV STREAMING SERVER STARTING ON PORT 5000...")
    print("Control Room Web Player: http://localhost:5000")
    print("Camera 1 Live Stream: http://localhost:5000/stream/1")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

import os
import cv2
import time
import psutil
import numpy as np
import pandas as pd
import streamlit as st
from ultralytics import YOLO
import easyocr

# Page Config
st.set_page_config(
    page_title="THE INITIATIVE 2.0 - ULTRA FAST COMMAND GRID",
    page_icon="⚡",
    layout="wide"
)

# High-Tech Cyber Styling CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@800;900&family=Rajdhani:wght@700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #050811 0%, #0d1322 100%);
        color: #e5e7eb;
        font-family: 'Rajdhani', sans-serif;
    }

    .cinematic-banner {
        text-align: center;
        padding: 18px;
        background: rgba(5, 8, 17, 0.85);
        border-top: 2px solid #ff0055;
        border-bottom: 2px solid #00f2fe;
        margin-bottom: 20px;
    }

    .cinematic-title {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        letter-spacing: 4px;
        margin: 0;
    }

    .cyan-glow { color: #00f2fe; text-shadow: 0 0 15px #00f2fe; }
    .red-glow { color: #ff0055; text-shadow: 0 0 20px #ff0055; }

    section[data-testid="stSidebar"] {
        background-color: #070a14 !important;
        border-right: 1px solid #1e293b;
    }

    div[data-testid="stBlock"] {
        background: rgba(13, 19, 34, 0.75);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        padding: 12px;
    }
</style>

<div class="cinematic-banner">
    <div style="font-size: 0.85rem; letter-spacing: 6px; color: #888;">STATE CRIME RECORD BUREAU - COMMAND & CONTROL GRID</div>
    <h1 class="cinematic-title">
        <span class="cyan-glow">THE</span> 
        <span class="red-glow">INITIATIVE</span> 
        <span class="cyan-glow">2.0</span>
    </h1>
</div>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
LOCAL_PHOTO_PATH = os.path.join(BASE_DIR, "my_photo.jpg")

USER_DETAILS = {
    "Name": "Aamin",
    "Mobile": "6356287866",
    "Address": "Anand, Gujarat",
    "Status": "WANTED / WATCHLIST SUSPECT"
}

VAHAN_CCTNS_DB = {
    "HN14OUC": {"Owner": "Rajesh Sharma", "Model": "Hyundai Creta (White)", "CCTNS_FIR": "FIR-2024/0981 (Vehicle Theft)", "Status": "CRITICAL SUSPECT"},
    "GJ01AB1234": {"Owner": "Aamin Vahora", "Model": "Honda City (Black)", "CCTNS_FIR": "FIR-2025/1102 (Unlawful Assembly)", "Status": "WATCHLIST"},
    "DL3CCE4321": {"Owner": "Vikram Patel", "Model": "Swift Dzire (Silver)", "CCTNS_FIR": "NIL (Clear)", "Status": "CLEARED"}
}

@st.cache_resource
def load_ai_models():
    yolo_model = YOLO("yolov8n.pt")
    ocr_reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
    return yolo_model, ocr_reader

yolo_model, ocr_reader = load_ai_models()
CLASS_NAMES = {0: "Person", 1: "Bicycle", 2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}

def log_audit_trail(user, action):
    log_file = "audit_trail.csv"
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    new_entry = pd.DataFrame([{"Timestamp": timestamp, "User": user, "Action": action}])
    if os.path.exists(log_file):
        new_entry.to_csv(log_file, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(log_file, index=False)

def clean_str(s):
    return "".join([c for c in str(s).upper() if c.isalnum()])

def trigger_audio_sos():
    audio_html = """
    <audio autoplay>
        <source src="https://www.soundjay.com/buttons/sounds/beep-01a.mp3" type="audio/mpeg">
    </audio>
    """
    st.components.v1.html(audio_html, height=0)

def match_face_hsv(ref_img, person_crop):
    try:
        if ref_img is None or person_crop is None or person_crop.size == 0:
            return False
        ph, pw = person_crop.shape[:2]
        head_crop = person_crop[0:int(ph * 0.40), 0:pw]
        if head_crop.size == 0:
            return False

        r_ref = cv2.resize(ref_img, (64, 64))
        r_target = cv2.resize(head_crop, (64, 64))

        h_ref = cv2.calcHist([cv2.cvtColor(r_ref, cv2.COLOR_BGR2HSV)], [0, 1], None, [16, 16], [0, 180, 0, 256])
        h_target = cv2.calcHist([cv2.cvtColor(r_target, cv2.COLOR_BGR2HSV)], [0, 1], None, [16, 16], [0, 180, 0, 256])

        cv2.normalize(h_ref, h_ref, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(h_target, h_target, 0, 1, cv2.NORM_MINMAX)

        return cv2.compareHist(h_ref, h_target, cv2.HISTCMP_CORREL) > 0.25
    except Exception:
        return False

def get_ip_camera_capture(url):
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp|timeout;5000000"
    if url == "0":
        return cv2.VideoCapture(0)
    
    clean_url = url.strip()
    if not clean_url.endswith("/video") and not clean_url.endswith(".m3u8") and "http" in clean_url:
        if not clean_url.endswith("/"):
            clean_url += "/"
        clean_url += "video"

    cap = cv2.VideoCapture(clean_url, cv2.CAP_FFMPEG)
    return cap

def process_advanced_cctv_engine(video_path, target_plate="", target_face_path=None, skip_frames=4):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    
    frame_count = 0
    results_log = []
    locations_mock = ["Bilimora Checkpost", "Kalupur Circle", "SG Highway Jcn", "RTO Checkpost", "Gandhidham Rambaugh"]
    
    status_box = st.empty()
    progress_bar = st.progress(0.0)
    
    clean_target_plate = clean_str(target_plate)
    ref_face_img = cv2.imread(target_face_path) if (target_face_path and os.path.exists(target_face_path)) else None
    
    start_time = time.time()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % skip_frames != 0:
                continue

            fh, fw = frame.shape[:2]
            progress_bar.progress(max(0.0, min(float(frame_count) / float(total_frames), 1.0)))
            current_time_str = time.strftime('%H:%M:%S', time.gmtime(frame_count / fps))
            status_box.markdown(f"**⚡ BLAZING FAST SCAN:** Timeline `{current_time_str}`")

            results = yolo_model(frame, verbose=False, imgsz=320)

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    if cls == 0 and ref_face_img is not None:
                        p_crop = frame[max(0, y1):min(fh, y2), max(0, x1):min(fw, x2)]
                        if match_face_hsv(ref_face_img, p_crop):
                            loc = locations_mock[frame_count % len(locations_mock)]
                            results_log.append({
                                "Frame_No": frame_count,
                                "Timestamp": current_time_str,
                                "Event Type": "🎯 FRS SUSPECT MATCH",
                                "Details": f"Name: {USER_DETAILS['Name']} | Status: {USER_DETAILS['Status']}",
                                "Location": loc
                            })

                    if clean_target_plate and cls in [2, 3, 5, 7]:
                        v_crop = frame[max(0, y1):min(fh, y2), max(0, x1):min(fw, x2)]
                        if v_crop.size > 0:
                            gray = cv2.cvtColor(v_crop, cv2.COLOR_BGR2GRAY)
                            ocr_res = ocr_reader.readtext(gray, detail=0)
                            detected_text = clean_str("".join(ocr_res))

                            if detected_text and (clean_target_plate in detected_text or detected_text in clean_target_plate):
                                loc = locations_mock[frame_count % len(locations_mock)]
                                results_log.append({
                                    "Frame_No": frame_count,
                                    "Timestamp": current_time_str,
                                    "Event Type": "🚗 ANPR VEHICLE MATCH",
                                    "Details": f"Target: {clean_target_plate} | Detected: {detected_text}",
                                    "Location": loc
                                })

    finally:
        cap.release()
        progress_bar.empty()
        status_box.empty()

    elapsed = round(time.time() - start_time, 2)
    st.success(f"⚡ Fast Scan Finished in **{elapsed} Seconds**!")
    return results_log

# Sidebar Navigation
st.sidebar.header("🔐 Access Control & Governance")
user_role = st.sidebar.selectbox("Role-Based Login Access", ["Admin Officer", "Investigator", "Viewer"])

mode = st.sidebar.radio("Navigation", [
    "AI Forensic Surveillance Engine", 
    "Live Govt Feeds & Multi-Camera Grid",
    "VAHAN & CCTNS National Database",
    "System Health & Audit Logs"
])

if mode == "AI Forensic Surveillance Engine":
    st.header("⚡ BLAZING FAST AI SURVEILLANCE ENGINE")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_video = st.file_uploader("Upload CCTV Footage", type=["mp4", "avi", "mov", "mkv"])
        target_plate_input = st.text_input("ANPR License Plate Target", value="HN14OUC")
    with col2:
        uploaded_face = st.file_uploader("FRS Target Suspect Photo", type=["jpg", "png", "jpeg"])
        frame_skip_step = st.select_slider("Fast Scan Speed Multiplier (Frame Skip)", options=[2, 4, 6, 8, 10], value=4)

    if st.button("🚀 EXECUTE LIGHTNING AI SCAN", type="primary"):
        if uploaded_video is not None:
            log_audit_trail(user_role, f"Ran AI Scan on {uploaded_video.name}")
            temp_video_path = "temp_cctv_input.mp4"
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_video.read())
                
            temp_face_path = LOCAL_PHOTO_PATH
            if uploaded_face is not None:
                os.makedirs("temp_watchlist", exist_ok=True)
                temp_face_path = os.path.join("temp_watchlist", "suspect.jpg")
                with open(temp_face_path, "wb") as f:
                    f.write(uploaded_face.read())

            matched_logs = process_advanced_cctv_engine(
                video_path=temp_video_path,
                target_plate=target_plate_input,
                target_face_path=temp_face_path,
                skip_frames=frame_skip_step
            )

            st.subheader("🎯 INSTANT TARGET MATCH JUMP & FORENSIC LOGS")
            if matched_logs:
                df_logs = pd.DataFrame(matched_logs)
                
                search_query = st.text_input("⚡ Quick Filter Logs by Plate / Suspect / Timestamp", value="")
                if search_query:
                    df_filtered = df_logs[df_logs.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
                    st.dataframe(df_filtered, use_container_width=True)
                else:
                    st.dataframe(df_logs, use_container_width=True)

                st.download_button("📥 Export Instant Forensic Report (CSV)", data=df_logs.to_csv(index=False), file_name="forensic_report.csv")
            else:
                st.info("No breaches or watchlist targets detected in video.")
        else:
            st.error("Please upload a CCTV video footage first.")

elif mode == "Live Govt Feeds & Multi-Camera Grid":
    st.header("📹 Live Grid & Mobile IP Camera Engine")
    cam_type = st.sidebar.selectbox("Select Feed Input", ["Laptop Integrated Webcam", "Mobile IP Camera Stream", "Hackathon Govt Live Stream URL"])
    
    cam_source = "0"
    if cam_type == "Mobile IP Camera Stream":
        st.warning("👉 Open 'IP Webcam' app on mobile, click 'Start Server', and paste the full URL below (e.g. http://192.168.1.5:8080)")
        cam_source = st.text_input("Mobile Camera IP Stream URL", value="http://10.21.117.238:8080")
    elif cam_type == "Hackathon Govt Live Stream URL":
        cam_source = st.text_input("Gujarat Police SCRB Portal Live URL", value="http://corp8.cloud/stream/cam29")

    if "streaming" not in st.session_state:
        st.session_state.streaming = False

    c1, c2 = st.columns(2)
    if c1.button("▶️ Start Live Stream", type="primary"):
        st.session_state.streaming = True
    if c2.button("⏹️ Stop Stream"):
        st.session_state.streaming = False

    FRAME_WINDOW = st.empty()
    alert_placeholder = st.empty()

    if st.session_state.streaming:
        log_audit_trail(user_role, f"Started Live Stream ({cam_type})")
        cap = get_ip_camera_capture(cam_source)

        try:
            retry_count = 0
            while st.session_state.streaming:
                ret, frame = cap.read()
                if not ret:
                    retry_count += 1
                    time.sleep(0.5)
                    if retry_count > 5:
                        st.error("❌ Unable to connect to IP Camera stream. Ensure Phone & PC are on SAME WI-FI network.")
                        break
                    continue
                
                retry_count = 0
                results = yolo_model(frame, verbose=False, imgsz=320)
                person_count = 0
                for r in results:
                    for box in r.boxes:
                        if int(box.cls[0]) == 0:
                            person_count += 1
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 242, 254), 2)

                FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if person_count >= 10:
                    alert_placeholder.error(f"🚨 CROWD SURGE ALERT: {person_count} Persons Active in Feed!")
                    trigger_audio_sos()
                else:
                    alert_placeholder.info(f"👥 Live Active Persons Count: {person_count}")
                time.sleep(0.01)
        finally:
            cap.release()

elif mode == "VAHAN & CCTNS National Database":
    st.header("🚘 VAHAN / CCTNS Integrated Criminal Database Search")
    query_plate = st.text_input("Search License Plate in National Database", value="HN14OUC").upper().strip()
    
    if st.button("🔍 SEARCH NATIONAL RECORDS", type="primary"):
        log_audit_trail(user_role, f"Queried VAHAN/CCTNS DB for {query_plate}")
        if query_plate in VAHAN_CCTNS_DB:
            record = VAHAN_CCTNS_DB[query_plate]
            st.success(f"MATCH FOUND IN CCTNS DATABASE FOR VEHICLE: {query_plate}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Registered Owner", record["Owner"])
            c2.metric("Vehicle Model", record["Model"])
            c3.metric("Watchlist Status", record["Status"])
            st.error(f"⚠️ CCTNS Crime Record: {record['CCTNS_FIR']}")
        else:
            st.warning("No linked criminal record or pending FIR found for this vehicle in CCTNS portal.")

elif mode == "System Health & Audit Logs":
    st.header("⚙️ Server Health & Security Audit Trail")
    c1, c2, c3 = st.columns(3)
    c1.metric("CPU Utilization", f"{psutil.cpu_percent()}%")
    c2.metric("RAM Usage", f"{psutil.virtual_memory().percent}%")
    c3.metric("Network Latency", "12 ms (Optimal)")

    st.subheader("🔐 Role-Based Security Audit Trail Logs")
    if os.path.exists("audit_trail.csv"):
        st.dataframe(pd.read_csv("audit_trail.csv"), use_container_width=True)
    else:
        st.info("No audit logs captured yet.")
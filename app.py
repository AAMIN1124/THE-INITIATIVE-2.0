import os
import cv2
import time
import torch
import numpy as np
import pandas as pd
import streamlit as st
from ultralytics import YOLO
import easyocr
from deepface import DeepFace

# Set Streamlit Page Config
st.set_page_config(
    page_title="Gujarat Police CCTV Analytics Platform",
    page_icon="🚨",
    layout="wide"
)

# Initialize and Cache Models
@st.cache_resource
def load_detection_models():
    # YOLOv8 for Vehicle & Person Detection
    yolo_model = YOLO("yolov8n.pt")
    # EasyOCR for License Plate Recognition
    ocr_reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
    return yolo_model, ocr_reader

yolo_model, ocr_reader = load_detection_models()

# Core Video Processing Engine
def process_cctv_stream(video_path, target_plate=None, target_face_path=None, frame_skip_sec=1):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    skip_frames = int(fps * frame_skip_sec)
    
    frame_count = 0
    results_log = []
    
    status_box = st.empty()
    progress_bar = st.progress(0)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        
        # Fast Scan Optimization: Process 1 frame per second
        if frame_count % skip_frames != 0:
            continue

        # Update Progress
        progress_bar.progress(min(frame_count / total_frames, 1.0))
        current_time_str = time.strftime('%H:%M:%S', time.gmtime(frame_count / fps))
        status_box.text(f"Scanning Video Timeline... Current Timestamp: {current_time_str}")

        # 1. ANPR Detection Logic
        if target_plate and len(target_plate.strip()) > 0:
            yolo_results = yolo_model(frame, verbose=False)
            for r in yolo_results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    # Class IDs for vehicles: 2 (car), 3 (motorcycle), 5 (bus), 7 (truck)
                    if cls in [2, 3, 5, 7]:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        vehicle_crop = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
                        
                        if vehicle_crop.size > 0:
                            ocr_res = ocr_reader.readtext(vehicle_crop)
                            for text_box in ocr_res:
                                detected_text = text_box[1].replace(" ", "").upper()
                                confidence = text_box[2]
                                
                                if target_plate.upper() in detected_text and confidence > 0.3:
                                    results_log.append({
                                        "Timestamp": current_time_str,
                                        "Event Type": "ANPR Match",
                                        "Target Detected": detected_text,
                                        "Confidence": f"{confidence * 100:.1f}%",
                                        "Frame ID": frame_count
                                    })

        # 2. Facial Recognition System (FRS) Logic
        if target_face_path and os.path.exists(target_face_path):
            try:
                # DeepFace verification against target face image
                dfs = DeepFace.find(
                    img_path=frame, 
                    db_path=os.path.dirname(target_face_path), 
                    enforce_detection=False, 
                    silent=True
                )
                if len(dfs) > 0 and not dfs[0].empty:
                    results_log.append({
                        "Timestamp": current_time_str,
                        "Event Type": "FRS Match",
                        "Target Detected": "Watchlist Suspect Identified",
                        "Confidence": "High",
                        "Frame ID": frame_count
                    })
            except Exception:
                pass

    cap.release()
    progress_bar.empty()
    status_box.empty()
    return results_log

# Streamlit Control Room UI Layout
st.title("🚨 Gujarat Police State Crime Record Bureau")
st.subheader("Automated CCTV Analytics & Forensic Search Platform")

# Sidebar Controls
st.sidebar.header("🎯 Investigation Control Panel")

uploaded_video = st.sidebar.file_uploader("Upload CCTV Footage / Stream File", type=["mp4", "avi", "mov", "mkv"])
target_plate_input = st.sidebar.text_input("Target License Plate Number (ANPR)", placeholder="e.g., GJ01AB1234")
uploaded_face = st.sidebar.file_uploader("Upload Target Person Photo (FRS)", type=["jpg", "png", "jpeg"])

scan_speed = st.sidebar.select_slider(
    "Scan Mode (Frame-Skipping Rate)",
    options=[0.5, 1.0, 2.0],
    value=1.0,
    help="1.0s = Fast Scan (1 frame per sec), 0.5s = Detailed Scan"
)

# Action Trigger
if st.sidebar.button("🔍 START AUTOMATED SEARCH", type="primary"):
    if uploaded_video is not None:
        # Save temp files for processing
        temp_video_path = "temp_cctv_input.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(uploaded_video.read())
            
        temp_face_path = None
        if uploaded_face is not None:
            os.makedirs("temp_watchlist", exist_ok=True)
            temp_face_path = os.path.join("temp_watchlist", "target_suspect.jpg")
            with open(temp_face_path, "wb") as f:
                f.write(uploaded_face.read())

        st.info("Initiating Fast Scan AI Engine across video timeline...")
        
        # Execute Search
        matched_logs = process_cctv_stream(
            video_path=temp_video_path,
            target_plate=target_plate_input,
            target_face_path=temp_face_path,
            frame_skip_sec=scan_speed
        )

        st.success("Analysis Complete!")

        # Display Results
        st.subheader("📋 Timestamped Forensic Log Results")
        if matched_logs:
            df_logs = pd.DataFrame(matched_logs)
            st.dataframe(df_logs, use_container_width=True)
            
            # Export CSV capability
            csv_data = df_logs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Official Forensic CSV Log",
                data=csv_data,
                file_name="cctv_forensic_investigation_report.csv",
                mime="text/csv"
            )
        else:
            st.warning("No matches detected for the specified target criteria in this footage.")
            
    else:
        st.error("Please upload a CCTV video file to initiate the search process.")
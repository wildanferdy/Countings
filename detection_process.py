# core/detection_process.py
import cv2
from ultralytics import YOLO
import os
import sys
from multiprocessing import Queue, Event
from queue import Empty
from datetime import datetime, timedelta

MAX_DISPLAY_WIDTH = 960
MAX_DISPLAY_HEIGHT = 720

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def detection_process(frame_q: Queue, result_q: Queue, stop_event: Event, initial_settings: dict):
    print(f"Detection process started with PID: {os.getpid()}")

    try:
        model = YOLO(resource_path('models/best1.pt'))
        result_q.put({"type": "model_ready"})
    except Exception as e:
        result_q.put({"type": "model_error", "error": str(e)})
        return

    settings = initial_settings
    vehicle_states = {}
    golongan_list = ["Gol 1", "Gol 2", "Gol 3", "Gol 4", "Gol 5", "Motor"]
    vehicle_counts = {golongan: {"In": 0, "Out": 0} for golongan in golongan_list}

    frame_num = 0
    pending_detections = []

    # --- Inisialisasi Time Offset ---
    if "start_timestamp_user" in settings and settings["start_timestamp_user"]:
        try:
            start_time = datetime.strptime(settings["start_timestamp_user"], "%Y-%m-%d %H:%M:%S")
            print(f"[INFO] Using custom start timestamp: {start_time}")
        except ValueError:
            print(f"[WARNING] Invalid start_timestamp_user: {settings['start_timestamp_user']}")
            start_time = datetime.now()
    else:
        start_time = datetime.now()

    while not stop_event.is_set():
        try:
            data = frame_q.get(timeout=0.05) # Mengurangi timeout untuk responsifitas lebih baik

            frame, new_settings = data

            if new_settings:
                settings = new_settings
                # --- Perbarui Time Offset jika Pengaturan Berubah ---
                if "start_timestamp_user" in settings and settings["start_timestamp_user"]:
                    try:
                        today_date = datetime.now().date()
                        user_dt_str = f"{today_date.year}-{today_date.month:02d}-{today_date.day:02d} {settings['start_timestamp_user'].split(' ')[1]}"
                        user_dt = datetime.strptime(user_dt_str, "%Y-%m-%d %H:%M:%S")
                        time_offset = user_dt - datetime.now()
                        print(f"Time offset updated to: {time_offset}")
                    except ValueError:
                        print(f"Invalid updated start_timestamp_user: {settings['start_timestamp_user']}")
                        time_offset = timedelta(seconds=0) # Reset to no offset if invalid
                else:
                    time_offset = timedelta(seconds=0) # Jika timestamp dihapus, reset offset
                # --- Akhir Perbarui Time Offset ---

            (h_orig, w_orig) = frame.shape[:2]

            line_offset_scaled = int(settings['line_offset'] * (h_orig / MAX_DISPLAY_HEIGHT))
            if settings['line_orientation'] == "Horizontal":
                line1_pos = int(settings['line1_y'] * (h_orig / MAX_DISPLAY_HEIGHT))
                line2_pos = line1_pos + line_offset_scaled
                # Gambar garis deteksi pada frame
                cv2.line(frame, (0, line1_pos), (w_orig, line1_pos), (0, 255, 0), 2)
                cv2.line(frame, (0, line2_pos), (w_orig, line2_pos), (0, 0, 255), 2)
            else: # Vertical
                line1_pos = int(settings['line1_x'] * (w_orig / MAX_DISPLAY_WIDTH))
                line2_pos = line1_pos + line_offset_scaled
                # Gambar garis deteksi pada frame
                cv2.line(frame, (line1_pos, 0), (line1_pos, h_orig), (0, 255, 0), 2)
                cv2.line(frame, (line2_pos, 0), (line2_pos, h_orig), (0, 0, 255), 2)

            results = model.track(frame, persist=True, tracker="bytetrack.yaml", conf=settings['confidence_threshold'], verbose=False)
            annotated_frame = results[0].plot()

            if results[0].boxes.id is not None:
                track_ids = results[0].boxes.id.int().cpu().tolist()
                class_ids = results[0].boxes.cls.int().cpu().tolist()
                boxes = results[0].boxes.xyxy.cpu()

                for i, track_id in enumerate(track_ids):
                    if track_id in vehicle_states:
                        vehicle_states[track_id]['last_seen'] = frame_num

                    if track_id in vehicle_states and not vehicle_states[track_id]['counted']:
                        initial_line = vehicle_states[track_id]['line']
                        direction_confirmed, direction = False, ""
                        vehicle_golongan = vehicle_states[track_id]['golongan']
                        trigger_point = int(boxes[i][3]) if settings['line_orientation'] == "Horizontal" else int((boxes[i][0] + boxes[i][2]) / 2)

                        if initial_line == 1 and abs(trigger_point - line2_pos) < 25:
                            if vehicle_golongan != "Unknown": vehicle_counts[vehicle_golongan]["In"] += 1
                            direction, direction_confirmed = "In", True
                        elif initial_line == 2 and abs(trigger_point - line1_pos) < 25:
                            if vehicle_golongan != "Unknown": vehicle_counts[vehicle_golongan]["Out"] += 1
                            direction, direction_confirmed = "Out", True

                        if direction_confirmed:
                            vehicle_states[track_id]['counted'] = True
                            # --- Terapkan Time Offset pada Timestamp Deteksi ---
                            timestamp = (start_time + timedelta(seconds=frame_num / 30)).strftime("%Y-%m-%d %H:%M:%S")
                            # --- Akhir Penerapan Time Offset ---
                            new_row = {"Timestamp": timestamp, "Vehicle ID": track_id, "Class": vehicle_golongan, "Direction": direction}
                            pending_detections.append(new_row)

                    elif track_id not in vehicle_states:
                        yolo_class_name = model.names[class_ids[i]]
                        golongan = yolo_class_name if yolo_class_name in vehicle_counts else "Unknown"
                        trigger_point = int(boxes[i][3]) if settings['line_orientation'] == "Horizontal" else int((boxes[i][0] + boxes[i][2]) / 2)

                        if abs(trigger_point - line1_pos) < 25:
                            vehicle_states[track_id] = {'line': 1, 'golongan': golongan, 'counted': False, 'last_seen': frame_num}
                        elif abs(trigger_point - line2_pos) < 25:
                            vehicle_states[track_id] = {'line': 2, 'golongan': golongan, 'counted': False, 'last_seen': frame_num}

            inactive_tracks = [tid for tid, data in vehicle_states.items() if frame_num - data.get('last_seen', frame_num) > 30]
            for tid in inactive_tracks:
                del vehicle_states[tid]

            result_q.put({"type": "frame", "image": annotated_frame})

            if pending_detections:
                result_q.put({
                    "type": "data_update",
                    "counts": vehicle_counts.copy(),
                    "new_rows": list(pending_detections)
                })
                pending_detections.clear()

            frame_num += 1
        except Empty:
            continue
        except Exception as e:
            print(f"Error in detection process: {e}")
            break
    print("Detection process received stop signal and is finishing.")
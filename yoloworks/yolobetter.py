from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
from ultralytics import YOLO
import numpy as np

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load YOLO model
model = YOLO("yolo11n.pt")

# Helper functions
def calculate_road_width(detections):
    road_edges = []
    for box, cls in detections:
        if int(cls) in [1, 2]:  # Road edges or lanes
            x1, y1, x2, y2 = map(int, box[:4])
            road_edges.append((x1 + x2) // 2)
    if len(road_edges) >= 2:
        road_edges.sort()
        return road_edges[-1] - road_edges[0]
    return None

def count_vehicles(detections):
    return sum(1 for _, cls in detections if int(cls) in [2, 3, 4])  # Vehicle IDs

def traffic_density(vehicle_count, frame_width, frame_height):
    frame_area = frame_width * frame_height
    return vehicle_count / frame_area if frame_area > 0 else 0

def calculate_speed(detections, prev_detections, frame_width, frame_height):
    total_speed = 0
    vehicle_count = 0
    if not prev_detections:
        return 0
    for (box, cls), (prev_box, prev_cls) in zip(detections, prev_detections):
        if int(cls) in [2, 3, 4]:
            x1, y1, x2, y2 = map(int, box[:4])
            prev_x1, prev_y1, prev_x2, prev_y2 = map(int, prev_box[:4])
            displacement = np.sqrt((x1 - prev_x1) ** 2 + (y1 - prev_y1) ** 2)
            speed = (displacement / frame_width) * 30  # Approximate speed
            total_speed += speed
            vehicle_count += 1
    return total_speed / vehicle_count if vehicle_count > 0 else 0

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_road_width, total_traffic_count, total_density, total_speed, frame_count = 0, 0, 0, 0, 0
    prev_detections = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        detections = results[0].boxes
        detections_filtered = [(box, cls) for box, cls in zip(detections.xyxy, detections.cls)]
        road_width = calculate_road_width(detections_filtered)
        traffic_count = count_vehicles(detections_filtered)
        speed = calculate_speed(detections_filtered, prev_detections, frame_width, frame_height)
        density = traffic_density(traffic_count, frame_width, frame_height)
        if road_width:
            total_road_width += road_width
        total_traffic_count += traffic_count
        total_speed += speed
        total_density += density
        frame_count += 1
        prev_detections = detections_filtered

    cap.release()
    avg_road_width = total_road_width / frame_count if frame_count > 0 else 0
    avg_traffic_count = total_traffic_count / frame_count if frame_count > 0 else 0
    avg_speed = total_speed / frame_count if frame_count > 0 else 0
    avg_density = total_density / frame_count if frame_count > 0 else 0
    return avg_road_width, avg_traffic_count, avg_speed, avg_density

# Flask route to process videos
@app.route('/process', methods=['POST'])
def process_videos():
    data = request.json
    video_paths = data.get('video_paths', [])
    road_metrics = []

    for video_path in video_paths:
        avg_road_width, avg_traffic_count, avg_speed, avg_density = process_video(video_path)
        road_metrics.append({
            "road_width": avg_road_width,
            "traffic_count": avg_traffic_count,
            "speed": avg_speed,
            "density": avg_density
        })

    # Calculate road scores
    road_scores = []
    for idx, metrics in enumerate(road_metrics):
        width, traffic, speed, density = metrics.values()
        width_traffic_ratio = (width / traffic) if traffic > 0 else width
        score = (0.5 * width_traffic_ratio) + (0.3 * speed) - (0.2 * density)
        road_scores.append({
            "road_id": idx + 1,
            "score": score,
            "metrics": metrics
        })

    # Sort by score
    road_scores.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({
        "road_scores": road_scores,
        "best_road": road_scores[0] if road_scores else None,
        "worst_road": road_scores[-1] if road_scores else None
    })

if __name__ == '__main__':
    app.run(debug=True)

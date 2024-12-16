from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import time
import cv2
import torch
import os

app = Flask(__name__)
CORS(app)

# Mapping route names to actual video file paths
route_to_video_path = {
    "route-1": r"C:\Users\USER\cand video 1.mp4",
    "route-2": r"C:\Users\USER\cand video 2.mp4",
    "route-3": r"C:\Users\USER\cand video 3.mp4",
    "route-4": r"C:\Users\USER\cand video 4.mp4"
}

# Load YOLOv5 model (or you can choose another version like YOLOv4 or YOLOv7 if needed)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # Load the YOLOv5 small model

# Function to process video with YOLO and extract data
def process_video_with_yolo(video_path):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise Exception(f"Could not open video {video_path}")

    frame_count = 0
    vehicle_count = 0
    speed_data = []
    road_width = 10  # Placeholder, you can update this with real road width detection logic
    
    # Loop over frames in the video
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # YOLO inference
        results = model(frame)

        # Filter out vehicles (car, bus, truck, etc.)
        vehicles = results.pandas().xywh[results.pandas().xywh['name'].isin(['car', 'bus', 'truck', 'motorbike'])]

        # Count the number of vehicles
        vehicle_count += len(vehicles)

        # Placeholder speed calculation (using random data for demonstration)
        speed_data.append(random.uniform(10, 80))  # Simulate speed in km/h

        frame_count += 1

    cap.release()
    
    if frame_count == 0:
        raise Exception(f"No frames processed for video {video_path}")
    
    # Calculate average speed from the collected speed data
    avg_speed = sum(speed_data) / len(speed_data)

    # Return a score and metrics based on detected objects and calculations
    score = random.uniform(0, 100)  # Random score based on the analysis
    metrics = {
        "road_width": road_width,  # Placeholder
        "vehicle_count": vehicle_count,
        "avg_speed": avg_speed,
        "density": vehicle_count / frame_count  # Simple density based on vehicles per frame
    }
    
    return score, metrics

@app.route('/process', methods=['POST'])
def process_request():
    try:
        data = request.get_json()
        print("Received data:", data)  # Log the received data

        if 'video_paths' not in data:
            return jsonify({"error": "video_paths is required"}), 400
        
        video_paths = data['video_paths']
        # Here, check the content of video_paths for debugging purposes
        print(f"Video paths: {video_paths}")

        # Your logic for video processing goes here
        # For now, returning a dummy response
        response = {
            "road_scores": [
                {"road_id": 1, "score": 85.6, "metrics": {"road_width": 8, "traffic_count": 12, "speed": 60, "density": 0.5}},
                {"road_id": 2, "score": 75.2, "metrics": {"road_width": 6, "traffic_count": 18, "speed": 50, "density": 0.7}}
            ],
            "best_road": {"road_id": 1},
            "worst_road": {"road_id": 2}
        }
        
        return jsonify(response)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


    # Identify the best and worst roads based on the score
    best_road = min(road_scores, key=lambda x: x["score"])  # Best road has the lowest score
    worst_road = max(road_scores, key=lambda x: x["score"])  # Worst road has the highest score

    # Prepare the response with comparison results
    response = {
        "road_scores": road_scores,
        "best_road": best_road,
        "worst_road": worst_road
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)


import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11n.pt")

# Paths for video files
video_paths = [
    r"C:\Users\USER\cand video 1.mp4",
    r"C:\Users\USER\cand video 2.mp4",
    r"C:\Users\USER\cand video 3.mp4",
    r"C:\Users\USER\cand video 4.mp4"
]

# Helper function to process a video and calculate metrics
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    # Metrics for road comparison
    total_road_width = 0
    total_traffic_count = 0
    total_speed = 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # If no more frames, exit loop

        # Perform object detection on the frame
        results = model(frame)  # Pass the frame to the YOLO model
        detections = results[0].boxes

        # Calculate road width using lane detection
        road_width = calculate_road_width(frame)
        
        # Calculate traffic count and speed
        traffic_count = count_vehicles(detections)
        speed = calculate_speed(detections)

        if road_width:
            total_road_width += road_width
        total_traffic_count += traffic_count
        total_speed += speed
        frame_count += 1

    cap.release()

    # Compute average road width, traffic count, and speed
    avg_road_width = total_road_width / frame_count if frame_count > 0 else 0
    avg_traffic_count = total_traffic_count / frame_count if frame_count > 0 else 0
    avg_speed = total_speed / frame_count if frame_count > 0 else 0

    return avg_road_width, avg_traffic_count, avg_speed

# Helper function to calculate road width using lane detection
def calculate_road_width(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)  # Edge detection

    # Hough Line Transform to detect lanes
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=100, maxLineGap=50)
    if lines is None:
        return None

    # Extract x-coordinates of lane lines
    lane_x_coords = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        lane_x_coords.extend([x1, x2])

    if len(lane_x_coords) < 2:
        return None

    # Sort and calculate width
    lane_x_coords.sort()
    road_width = lane_x_coords[-1] - lane_x_coords[0]
    return road_width

# Helper function to count vehicles on a road
def count_vehicles(detections):
    vehicle_count = 0
    for box, cls in zip(detections.xyxy, detections.cls):
        if int(cls) in [2, 3, 4]:  # Match class IDs for vehicles (e.g., car, truck, bike)
            vehicle_count += 1
    return vehicle_count

# Helper function to calculate speed of vehicles (mock implementation)
def calculate_speed(detections):
    # Mock speed calculation: Average speed per vehicle in a frame (randomized for demonstration)
    # Replace this with real speed estimation logic if needed
    return sum(np.random.uniform(10, 30) for _ in detections.cls if int(_) in [2, 3, 4])

# Process all videos
road_metrics = []
for video_path in video_paths:
    avg_road_width, avg_traffic_count, avg_speed = process_video(video_path)
    road_metrics.append((avg_road_width, avg_traffic_count, avg_speed))

# Adjust weights: Width-Traffic ratio (70%) and Speed (30%)
WIDTH_TRAFFIC_WEIGHT = 0.7
SPEED_WEIGHT = 0.3

# Scoring formula: Combine normalized width/traffic and speed
def calculate_score(width, traffic, speed):
    width_traffic_ratio = width / traffic if traffic > 0 else width
    return (WIDTH_TRAFFIC_WEIGHT * width_traffic_ratio) + (SPEED_WEIGHT * speed)

# Calculate scores for all roads
road_scores = []
for idx, (width, traffic, speed) in enumerate(road_metrics):
    score = calculate_score(width, traffic, speed)
    road_scores.append((idx + 1, score, width, traffic, speed))

# Find the road with the best score
road_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by score (descending)
best_road = road_scores[0]

# Display the comparison results
for road_id, score, width, traffic, speed in road_scores:
    print(f"Road {road_id}: Width = {width:.2f}, Traffic = {traffic:.2f}, Speed = {speed:.2f}, Score = {score:.2f}")

print(f"Better Road: Road {best_road[0]} with Score = {best_road[1]:.2f}")

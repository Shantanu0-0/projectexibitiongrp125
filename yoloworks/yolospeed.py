import cv2
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

    # Get video frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

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

        # Calculate road width, traffic count, and vehicle speed for the current frame
        road_width = calculate_road_width(detections)
        traffic_count = count_vehicles(detections)
        avg_speed = calculate_average_speed(detections, fps)

        if road_width:
            total_road_width += road_width
        total_traffic_count += traffic_count
        total_speed += avg_speed
        frame_count += 1

    cap.release()

    # Compute average road width, traffic count, and speed
    avg_road_width = total_road_width / frame_count if frame_count > 0 else 0
    avg_traffic_count = total_traffic_count / frame_count if frame_count > 0 else 0
    avg_vehicle_speed = total_speed / frame_count if frame_count > 0 else 0

    return avg_road_width, avg_traffic_count, avg_vehicle_speed

# Helper function to calculate road width in pixels
def calculate_road_width(detections):
    road_edges = []
    for box, cls in zip(detections.xyxy, detections.cls):
        if int(cls) in [1, 2]:  # Match class ID for road edges or lanes
            x1, y1, x2, y2 = map(int, box[:4])  # Bounding box coordinates
            road_edges.append((x1 + x2) // 2)  # Take the horizontal center of the edge

    if len(road_edges) >= 2:
        road_edges.sort()
        road_width = road_edges[-1] - road_edges[0]
        return road_width
    return None

# Helper function to count vehicles on a road
def count_vehicles(detections):
    vehicle_count = 0
    for box, cls in zip(detections.xyxy, detections.cls):
        if int(cls) in [2, 3, 4]:  # Match class IDs for vehicles (e.g., car, truck, bike)
            vehicle_count += 1
    return vehicle_count

# Helper function to calculate average speed of vehicles
def calculate_average_speed(detections, fps):
    total_speed = 0
    vehicle_count = 0

    for box, cls in zip(detections.xyxy, detections.cls):
        if int(cls) in [2, 3, 4]:  # Match class IDs for vehicles (e.g., car, truck, bike)
            x1, y1, x2, y2 = map(int, box[:4])
            speed = (x2 - x1) * fps  # Estimate speed based on bounding box width
            total_speed += speed
            vehicle_count += 1

    return total_speed / vehicle_count if vehicle_count > 0 else 0

# Process all videos
road_metrics = []
for video_path in video_paths:
    avg_road_width, avg_traffic_count, avg_vehicle_speed = process_video(video_path)
    road_metrics.append((avg_road_width, avg_traffic_count, avg_vehicle_speed))

# Calculate road scores and determine the best road
road_scores = []
for idx, (width, traffic, speed) in enumerate(road_metrics):
    width_traffic_ratio = width / traffic if traffic > 0 else width
    score = 0.5 * width_traffic_ratio + 0.5 * speed
    road_scores.append((idx + 1, score, width, traffic, speed))

# Find the road with the best score
road_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by score (descending)
best_road = road_scores[0]

# Display the comparison results
for road_id, score, width, traffic, speed in road_scores:
    print(f"Road {road_id}: Width = {width}, Traffic = {traffic}, Speed = {speed:.2f}, Score = {score:.2f}")

print(f"Better Road: Road {best_road[0]} with Score = {best_road[1]:.2f}")

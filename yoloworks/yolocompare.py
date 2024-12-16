import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11n.pt")

# Paths for two video files
video_path_1 = r"C:\Users\USER\shreya1.mp4"
video_path_2 = r"C:\Users\USER\Untitled video - Made with Clipchamp (1).mp4"

# Helper function to process a video and calculate metrics
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    # Get video frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Metrics for road comparison
    total_road_width = 0
    total_traffic_count = 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # If no more frames, exit loop

        # Perform object detection on the frame
        results = model(frame)  # Pass the frame to the YOLO model
        detections = results[0].boxes

        # Calculate road width and traffic count for the current frame
        road_width = calculate_road_width(detections)
        traffic_count = count_vehicles(detections)

        if road_width:
            total_road_width += road_width
        total_traffic_count += traffic_count
        frame_count += 1

    cap.release()

    # Compute average road width and traffic count
    avg_road_width = total_road_width / frame_count if frame_count > 0 else 0
    avg_traffic_count = total_traffic_count / frame_count if frame_count > 0 else 0

    return avg_road_width, avg_traffic_count

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

# Process both videos
road1_width, road1_traffic = process_video(video_path_1)
road2_width, road2_traffic = process_video(video_path_2)

# Calculate road ratios
road1_ratio = road1_width / road1_traffic if road1_traffic > 0 else road1_width
road2_ratio = road2_width / road2_traffic if road2_traffic > 0 else road2_width

# Determine the better road
if road1_ratio > road2_ratio:
    better_road = "Road 1"
elif road1_ratio < road2_ratio:
    better_road = "Road 2"
else:
    better_road = "Tie or cannot determine"

# Display the comparison results
print(f"Road 1: Width = {road1_width}, Traffic = {road1_traffic}, Ratio = {road1_ratio:.2f}")
print(f"Road 2: Width = {road2_width}, Traffic = {road2_traffic}, Ratio = {road2_ratio:.2f}")
print(f"Better Road: {better_road}")


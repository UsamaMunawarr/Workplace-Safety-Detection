from ultralytics import YOLO
import cv2
import cvzone
import math
import os

# ----------------------------------------------------------
# 1️⃣ Input video path (change this to your video file)
# ----------------------------------------------------------
input_video = "ppe-1-1.mp4"  # 👈 your video name or path here

if not os.path.exists(input_video):
    raise FileNotFoundError(f"❌ Video file not found: {input_video}")

# ----------------------------------------------------------
# 2️⃣ Output setup: save result in same folder
# ----------------------------------------------------------
output_video = os.path.splitext(input_video)[0] + "_detections.avi"

# ----------------------------------------------------------
# 3️⃣ Load YOLOv8 model (make sure 'ppe.pt' is in the same folder)
# ----------------------------------------------------------
model = YOLO("ppe.pt")

# ----------------------------------------------------------
# 4️⃣ Open video file
# ----------------------------------------------------------
cap = cv2.VideoCapture(input_video)
if not cap.isOpened():
    raise RuntimeError("❌ Could not open video file.")

# Get frame size and FPS to save output properly
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Define video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec
out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))

print(f"🎬 Processing video: {input_video}")
print(f"💾 Output will be saved as: {output_video}")

# ----------------------------------------------------------
# 5️⃣ PPE class labels
# ----------------------------------------------------------
classNames = [
    'Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask',
    'NO-Safety Vest', 'Person', 'Safety Cone',
    'Safety Vest', 'machinery', 'vehicle'
]

# ----------------------------------------------------------
# 6️⃣ Frame-by-frame processing
# ----------------------------------------------------------
while True:
    success, img = cap.read()
    if not success:
        print("✅ Video processing complete.")
        break

    # YOLO detection
    results = model(img, stream=True)

    # Loop through detections
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            currentClass = classNames[cls]

            # Color code
            if conf > 0.5:
                if currentClass in ['Hardhat', 'Mask', 'Safety Vest']:
                    myColor = (0, 255, 0)   # ✅ Safe
                elif currentClass in ['NO-Hardhat', 'NO-Mask', 'NO-Safety Vest']:
                    myColor = (0, 0, 255)   # ❌ Unsafe
                else:
                    myColor = (255, 0, 0)   # Other

                # Draw rectangle + label
                cv2.rectangle(img, (x1, y1), (x2, y2), myColor, 3)
                cvzone.putTextRect(
                    img, f'{currentClass} {conf}',
                    (max(0, x1), max(35, y1)),
                    scale=0.7, thickness=1,
                    colorB=myColor, colorT=(255, 255, 255),
                    colorR=myColor, offset=5
                )

    # Write the processed frame to the output video
    out.write(img)

    # Optional: show live progress
    cv2.imshow("PPE Detection (Press 'q' to quit)", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("🛑 Stopped by user.")
        break

# ----------------------------------------------------------
# 7️⃣ Clean up
# ----------------------------------------------------------
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"✅ Saved processed video to: {output_video}")

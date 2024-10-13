from ultralytics import YOLO
import cv2
import numpy as np
from matplotlib import pyplot as plt
import math
import os
from pathlib import Path
from image_services.image_utils import CV2Colors, np_array_to_byte_image
import base64


model = YOLO("./src/ml_services/runs/detect/train/weights/best.pt")

def get_detected_nuts_bolts(image):
    processed_images = model.predict(
        [image], 
        conf=0.2, 
        show_conf=False, 
        show_boxes=False,
        show_labels=False
    )

    detected_nuts_bolts = None
    for processed_image in processed_images:
        detected_nuts_bolts = processed_image.boxes
    
    return detected_nuts_bolts
        

def get_safe_coordinates(image, detected_object, scale=0.1):
    image_height, image_width, _ = image.shape
    x1, y1, x2, y2 = list(map(lambda x: x.item(), detected_object.xyxyn[0]))

    # Get Actual Coordinates
    x1, y1, x2, y2 = x1*image_width, y1*image_height, x2*image_width, y2*image_height
    obj_width, obj_height = x2-x1, y2-y1
    xc, yc = int(x1 + obj_width/2), int(y1 + obj_height/2)

    x1 = int(x1-scale*obj_width) if x1-scale*obj_width > 0 else 0
    y1 = int(y1-scale*obj_height) if y1-scale*obj_height > 0 else 0
    x2 = int(x2+scale*obj_width) if x2+scale*obj_width < image_width else image_width
    y2 = int(y2+scale*obj_height) if y2+scale*obj_height < image_height else image_height

    return (x1, y1, x2, y2, xc, yc)


def calculate_contour_angle(contour, center):
    leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
    rightmost = tuple(contour[contour[:, :, 0].argmax()][0])

    # Calculate angles relative to center using arctan2
    angle_left = math.degrees(math.atan2(leftmost[1] - center[1], leftmost[0] - center[0]))
    angle_right = math.degrees(math.atan2(rightmost[1] - center[1], rightmost[0] - center[0]))

    # Calculate the angle between the two points (difference between left and right angles)
    theta = abs(angle_left - angle_right)
    return theta


def are_contours_collinear(center_point, contours, tolerance=0.01):
    if len(contours) < 2:
        return False

    [vx, vy, x, y] = cv2.fitLine(contours[0], cv2.DIST_L2, 0, 0.01, 0.01)
    initial_direction = (vx, vy)
    
    for contour in contours:
        # Fit a line to each contour
        [vx, vy, x, y] = cv2.fitLine(contour, cv2.DIST_L2, 0, 0.01, 0.01)
        direction = (vx, vy)
        
        # Check if the direction vectors are within the tolerance
        if not (np.isclose(direction[0], initial_direction[0], atol=tolerance) and
                np.isclose(direction[1], initial_direction[1], atol=tolerance)):
            return False
    
    return True


def closest_contour_to_point(contours, point):
    min_dist = float('inf')
    nearest_contour = None

    for contour in contours:
        # Get the nearest point on the contour to the center
        distance = cv2.pointPolygonTest(contour, point, True)
        
        if distance < 0:
            distance = abs(distance)

        if distance < min_dist:
            min_dist = distance
            nearest_contour = contour
    
    return nearest_contour


def painted_contours_in_region_of_interest(image, x1, y1, x2, y2):
    roi = image[y1:y2, x1:x2]
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # Apply a binary threshold to isolate white regions
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours


def get_alignment_checked_image(image_data):
    image_data = base64.b64decode(image_data)
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    result_image = image.copy()

    detected_nuts_bolts = get_detected_nuts_bolts(image)

    total_nut_bolts = len(detected_nuts_bolts)
    aligned_nuts_bolts = misaligned_nuts_bolts = non_marked_nuts_bolts = 0

    for nut_bolt in detected_nuts_bolts:
        x1, y1, x2, y2, xc, yc = get_safe_coordinates(image, nut_bolt, 0.2)
        center = (xc, yc)

        contours = painted_contours_in_region_of_interest(image, x1, y1, x2, y2)

        # Filter contours by size to remove unwanted small/large contours (like edges of nuts)
        filtered_contours = [cnt+np.array([x1, y1]) for cnt in contours if 50 < cv2.contourArea(cnt) < 500]

        filtered_contours_final_adjusted = []
        if (len(filtered_contours)) >= 1:
            closest_contour = closest_contour_to_point(filtered_contours, center)
            filtered_contours_final_adjusted.append(closest_contour)
        
        for contour in filtered_contours:
            theta = calculate_contour_angle(contour, center)

            if theta < 15:
                filtered_contours_final_adjusted.append(contour)
        
        colors = CV2Colors.RED
        alignment_text = "Non-Marked"
        if len(filtered_contours_final_adjusted) <= 1:
            non_marked_nuts_bolts += 1
        else:
            contours_collinear = are_contours_collinear(center, filtered_contours_final_adjusted, 0.5)
            if contours_collinear:
                aligned_nuts_bolts += 1
                colors = CV2Colors.GREEN
                alignment_text = "Aligned"
            else:
                misaligned_nuts_bolts += 1
                colors = CV2Colors.YELLOW
                alignment_text = "Misaligned"

        cv2.putText(result_image, alignment_text, (x1, yc), cv2.FONT_HERSHEY_SIMPLEX, 1, colors, 2)
        cv2.drawContours(result_image, filtered_contours_final_adjusted, -1, colors, 2)
        cv2.rectangle(result_image, (x1, y1), (x2, y2), colors, thickness=2)
    
    # plt.title('Detected White Paint Marks')
    # plt.imshow(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
    # plt.show()
    
    return (np_array_to_byte_image(result_image), total_nut_bolts, aligned_nuts_bolts, misaligned_nuts_bolts, non_marked_nuts_bolts)


# get_alignment_checked_image(image_path)

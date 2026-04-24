import cv2
import json
import requests
from pyzbar.pyzbar import decode
from time import sleep, time

from arduino_interface import ArduinoInterface
from main import API_URL, ConveyorController, east_coast, west_coast
from adafruit_servokit import ServoKit
import busio


DETECT_CAMERA_INDEX = 1
QR_CAMERA_INDEX = 2
QR_READ_TIMEOUT = 2.0
PRE_SCAN_RUN_SECONDS = 2.5
SERVO_DELAY = 1.0
SERVO_CHANNEL = 0


def detect_box(frame, min_area=4000):
    """Detect a box against a light background and return its bounding rectangle."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # White-background setup: keep darker/saturated foreground objects.
    lower = (5, 30, 20)
    upper = (35, 255, 220)
    mask = cv2.inRange(hsv, lower, upper)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best_rect = None
    best_area = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        if h == 0:
            continue

        aspect_ratio = w / float(h)
        rect_area = w * h
        fill_ratio = area / float(rect_area) if rect_area else 0.0

        if 0.5 <= aspect_ratio <= 2.5 and fill_ratio >= 0.45 and area > best_area:
            best_rect = (x, y, w, h)
            best_area = area

    return best_rect, mask


def parse_package(data):
    package = json.loads(data)
    pkg_id = package.get("pkg_id", "")
    name = package.get("name", "")
    street_address = package.get("street_address", "")
    city = package.get("city", "")
    state = package.get("state", "")
    zip_code = package.get("zip_code", "")
    weight = package.get("weight", "")

    if state in east_coast:
        direction = "east"
        region = "EAST"
    elif state in west_coast:
        direction = "west"
        region = "WEST"
    else:
        direction = "center"
        region = "OTHER"

    address = ", ".join(
        part for part in [street_address, city, f"{state} {zip_code}".strip()]
        if part.strip()
    )

    payload = {
        "Package ID": pkg_id,
        "name": name,
        "address": address,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "weight": weight,
        "region": region,
    }
    return direction, payload


def main():
    detect_camera = cv2.VideoCapture(DETECT_CAMERA_INDEX)
    qr_camera = cv2.VideoCapture(QR_CAMERA_INDEX)
    arduino = ArduinoInterface(port='/dev/ttyACM0')
    conveyor = ConveyorController(arduino)
    i2c = busio.I2C(3, 2)
    kit = ServoKit(channels=16, i2c=i2c)
    kit.servo[SERVO_CHANNEL].set_pulse_width_range(500, 2500)

    if not detect_camera.isOpened():
        print(f"Error: Could not open detection camera at index {DETECT_CAMERA_INDEX}.")
        return

    if not qr_camera.isOpened():
        print(f"Error: Could not open QR camera at index {QR_CAMERA_INDEX}.")
        detect_camera.release()
        return

    package_detected = False
    detection_start_time = None
    last_qr_data = None
    last_conveyor_start_time = time()

    conveyor.start()

    while True:
        detect_ok, detect_frame = detect_camera.read()
        qr_ok, qr_frame = qr_camera.read()
        if not detect_ok or not qr_ok:
            break

        ready_to_scan = (time() - last_conveyor_start_time) >= PRE_SCAN_RUN_SECONDS
        box_rect, mask = detect_box(detect_frame) if ready_to_scan else (None, None)

        if box_rect is not None:
            x, y, w, h = box_rect
            cv2.rectangle(detect_frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(
                detect_frame,
                "Box ROI",
                (x, max(20, y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )

        if not package_detected and ready_to_scan and box_rect is not None:
            package_detected = True
            detection_start_time = time()
            last_qr_data = None
            conveyor.stop()
            print("Box detected by detection camera. Conveyor stopped. Waiting for QR code...")

        if package_detected:
            elapsed = time() - detection_start_time
            qr_codes = decode(qr_frame)
            if qr_codes:
                last_qr_data = qr_codes[0].data.decode("utf-8")

                points = qr_codes[0].polygon
                if points:
                    pts = [(point.x, point.y) for point in points]
                    for index in range(len(pts)):
                        cv2.line(qr_frame, pts[index], pts[(index + 1) % len(pts)], (0, 255, 0), 3)

            if last_qr_data or elapsed >= QR_READ_TIMEOUT:
                if not last_qr_data:
                    print("No QR code detected in 2 seconds. Resuming conveyor.\n")
                    conveyor.start()
                    last_conveyor_start_time = time()
                    package_detected = False
                    detection_start_time = None
                    continue

                print("Package data: " + last_qr_data)
                try:
                    direction, payload = parse_package(last_qr_data)
                    print("State: " + payload["state"])
                    print(f"Package going to {payload['region']}\n")

                    requests.post(API_URL, json=payload)

                except json.JSONDecodeError:
                    print("Error: QR code data is not valid JSON\n")
                    direction = "center"

                if direction == "east":
                    sleep(SERVO_DELAY)
                    kit.servo[SERVO_CHANNEL].angle = 140
                    sleep(10)
                    kit.servo[SERVO_CHANNEL].angle = 180
                    sleep(10)
                elif direction == "west":
                    sleep(SERVO_DELAY)
                    kit.servo[SERVO_CHANNEL].angle = 55
                    sleep(1)
                    kit.servo[SERVO_CHANNEL].angle = 180
                    sleep(0.5)
                else:
                    sleep(SERVO_DELAY)
                    kit.servo[SERVO_CHANNEL].angle = 180
                    sleep(1)

                conveyor.start()
                last_conveyor_start_time = time()

                package_detected = False
                detection_start_time = None
                last_qr_data = None

        cv2.imshow("Detection Camera", detect_frame)
        cv2.imshow("QR Camera", qr_frame)
        if mask is not None:
            cv2.imshow("Detection Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    detect_camera.release()
    qr_camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
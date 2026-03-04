# program to detect and decode qr codes 

# importing OpenCV package
import cv2

# defining what camera is capturing footage
camera = cv2.VideoCapture(0)

# creating a QR code detector object
detector = cv2.QRCodeDetector()

# loop runs forever until we break out of it (with esc key)
while True:
    # read a frame from the camera
    # success = True if frame was grabbed, frame = the actual image
    success, frame = camera.read()
    
    # if no frame, stop loop
    if not success:
        break

    # try to find and decode a QR code in the frame
    # data = decoded text, other two values we don't need
    data, _, _ = detector.detectAndDecode(frame)

    # if a QR code was found and decoded, print the data
    if data:
        print(data)

    # show the live camera feed in a window called "QR Scanner"
    cv2.imshow("QR Decoder", frame)

    # wait 1ms for a key press, if the user presses 'esc' then stop the loop
    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()

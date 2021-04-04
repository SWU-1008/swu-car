import cv2

capture = cv2.VideoCapture(2)
frame_count = capture.get(cv2.CAP_PROP_FPS)
frame_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
frame_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
print(frame_count, frame_width, frame_height)
while True:
    ret, frame = capture.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break

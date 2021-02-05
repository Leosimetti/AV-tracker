import time
import cv2

# PARAMETERS OF VIDEO CAPTURING
DEBUG = True
FILENAME = 'video.avi'
FRAMERATE = 20.0
RESOLUTION = (640, 480)
EXIT_KEYS = ['q', 'Q']
REGULATE_TIME = True

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)  # Choose video camera interface?

    # Video codec
    # TODO Test on different platforms
    fourCC = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(FILENAME, fourCC, FRAMERATE, RESOLUTION)

    start_time = time.time()
    capture_duration = 5

    while cap.isOpened():
        if REGULATE_TIME & int(time.time() - start_time) > capture_duration:
            out = cv2.VideoWriter(FILENAME, fourCC, FRAMERATE, RESOLUTION)

        ret, frame = cap.read()

        if ret:
            # Write frame to video file
            out.write(frame)

            if DEBUG:
                # Show video
                cv2.imshow('frame', frame)

                # Stop program on exit key
                if cv2.waitKey(1) & 0xFF in [ord(i) for i in EXIT_KEYS]:
                    break
        else:
            break

    # Release everything
    out.release()
    cap.release()
    cv2.destroyAllWindows()

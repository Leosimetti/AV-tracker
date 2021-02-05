import numpy as np
import cv2

# PARAMETERS OF VIDEO
DEBUG = True
FILENAME = 'video.avi'
FRAMERATE = 20.0
RESOLUTION = (640, 480)
EXIT_KEYS = ['q', 'Q', 'й', "Й"]

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    # Video codec
    # TODO Test on different platforms
    fourCC = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(FILENAME, fourCC, FRAMERATE, RESOLUTION)

    while cap.isOpened():
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

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

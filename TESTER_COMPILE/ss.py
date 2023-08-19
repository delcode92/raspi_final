import multiprocessing
import cv2

class IPCam:
    def __init__(self) -> None:
        print("IPCAM PROC... }")
        # Open a connection to the default camera (index 0)
        cap = cv2.VideoCapture('http://192.168.100.69:4747/video')

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        while True:
            # Read a frame from the camera
            ret, frame = cap.read()

            if not ret:
                print("Error: Could not read frame.")
                break

            # Display the frame in a window
            cv2.imshow('Webcam', frame)

            # Check for the 'q' key to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the camera and close the window
        cap.release()
        cv2.destroyAllWindows()

class Server:
    def __init__(self) -> None:
        print("SERVER PROC... }")

def run():
    conn1, conn2 = multiprocessing.Pipe()
    process_1 = multiprocessing.Process(target=IPCam, name="IPCAM")
    process_2 = multiprocessing.Process(target=Server, name="SERVER")

    multiprocessing.freeze_support()
    process_1.start()
    process_2.start()
    process_1.join()
    process_2.join()

if __name__ == "__main__":
    run()

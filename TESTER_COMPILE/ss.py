import multiprocessing
import cv2

class IPCam:
    def __init__(self) -> None:
        print("IPCAM PROC... }")

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
    # process_1.join()
    # process_2.join()

if __name__ == "__main__":
    run()

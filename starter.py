from multiprocessing import Process
import time

def run_charter():
    import PressureController

if __name__ == "__main__":
    p1 = Process(target=run_charter)
    p1.start()
    p1.join()

    #print("Hello")
    time.sleep(100)
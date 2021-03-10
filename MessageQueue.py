from multiprocessing import Queue, Process, active_children, current_process
from time import sleep, time
from queue import Empty
from random import uniform

# Constants
DIRECTION_ZERO = 3
DIRECTION_ONE = 3
BRIDGE_CAPACITY = 3 


def produce_direction(direction, direction_queue, confirm_queue, road_queue):
    number_of_cars = DIRECTION_ZERO if direction == 0 else DIRECTION_ONE

    for number in range(number_of_cars):
        licence_plate = str(direction) + str(number)
        car = Process(target=cross_the_bridge, args=(licence_plate, direction_queue, confirm_queue, bridge_queue))
        car.start()


def cross_the_bridge(licence_plate, direction_queue, confirm_queue, bridge_queue):
    # Sleep 
    sleep(uniform(0.1, 2.0))
    # print(licence_plate, "WOKE UP")

    # Wait for the bridge
    message = direction_queue.get(timeout=None)
    print(licence_plate, "recieves -", message)

    # Approve car 
    message = licence_plate + " approved to go over bridge."
    print(licence_plate, "sends -", message)
    confirm_queue.put(message)

    # List it as a car going over bridge
    message = licence_plate
    print(licence_plate,"sends -", message)
    bridge_queue.put(message)

    print("------ DONE ------ cross_the_bridge -", licence_plate)


def get_cars_to_the_other_side(direction_zero_queue, direction_one_queue, confirm_queue, bridge_queue):
    direction_is_zero = True
    while True:
        direction_is_zero = not direction_is_zero
        approve_cars(
            capacity=[BRIDGE_CAPACITY], 
            direction_queue=direction_zero_queue if direction_is_zero else direction_one_queue, 
            confirm_queue=confirm_queue
        )
        simulate_crossing(bridge_queue)

        if  .empty():
            print("There is no more cars.")
            break
        
        print("------ DONE ------ get_cars_to_the_other_side - ITERATION")

    print("------ DONE ------ get_cars_to_the_other_side")

def get_cars_to_the_other_side(direction_zero_queue, direction_one_queue, confirm_queue, bridge_queue):

    while True:
        capacity = [BRIDGE_CAPACITY]

        while direction_one_queue.empty() and capacity[0] > 2:
            if handshake(direction_one_queue, confirm_queue):
                capacity[0] = capacity[0] - 1
            else:
                break

        while direction_one_queue.empty() and capacity[0] > 1:
            if handshake(direction_one_queue, confirm_queue):
                capacity[0] = capacity[0] - 1
        
        while direction_one_queue.empty() and capacity[0] > 0:
            if handshake(direction_one_queue, confirm_queue):
                capacity[0] = capacity[0] - 1
        
        sleep(uniform(1.0, 3.0))
        print("Cars which crossed over are: ")
        while not bridge_queue.empty():
            message = bridge_queue.get()
            print("Bridge receives - " + message)
        
        print("------ DONE ------ simulate_crossing")

        capacity = [BRIDGE_CAPACITY]

        while direction_zero_queue.empty() and capacity[0] > 2:
            if handshake(direction_zero_queue, confirm_queue):
                capacity[0] = capacity[0] - 1
            else:
                break

        while direction_zero_queue.empty() and capacity[0] > 1:
            if handshake(direction_zero_queue, confirm_queue):
                capacity[0] = capacity[0] - 1
        
        while direction_zero_queue.empty() and capacity[0] > 0:
            if handshake(direction_zero_queue, confirm_queue):
                capacity[0] = capacity[0] - 1
        
        sleep(uniform(1.0, 3.0))
        print("Cars which crossed over are: ")
        while not bridge_queue.empty():
            message = bridge_queue.get()
            print("Bridge receives - " + message)
        
        print("------ DONE ------ simulate_crossing")

        if (capacity[0] == BRIDGE_CAPACITY):
            print("There is no more cars.")
            break
        print("------ DONE ------ get_cars_to_the_other_side - ITERATION")
        break
    print("------ DONE ------ get_cars_to_the_other_side")
        

def approve_cars(capacity, direction_queue, confirm_queue):
    start_time = time()
    direction_time_limit = uniform(0.5, 1.0)
    while capacity[0] > 0 and (time() - start_time) < direction_time_limit:
        if handshake(direction_queue, confirm_queue):
            capacity[0] -= 1
        else:
            break
    print("Time's up?", str((time() - start_time) < direction_time_limit))

def handshake(direction_queue, confirm_queue):
    message = "Bridge: the car is approved to go over."
    print("Bridge sends -", message)
    direction_queue.put(message)
    try:
        message = confirm_queue.get(timeout=None)
        print("Bridge recieves -", message)
        return True
    except Empty:
        return False 
        
def simulate_crossing(bridge_queue):
    sleep(uniform(1.0, 3.0))
    print("Cars which crossed over are: ")
    while not bridge_queue.empty():
        message = bridge_queue.get()
        print("Bridge receives - " + message)
    
    print("------ DONE ------ simulate_crossing")


def terminate_finished_processes():
    print("GOT INTO TERMINATE FINISHED")
    for child in active_children():
        print("GOT IN FOR LOOP", str(child.pid))
        child.join()
        print("Child process", str(child.pid), "joined.")      
    print("------ DONE ------ terminate_finished_processes")  


if __name__ == '__main__':
    direction_zero_queue = Queue(1)
    direction_one_queue = Queue(1)
    confirm_queue = Queue(1)
    bridge_queue = Queue(BRIDGE_CAPACITY)

    produce_direction(0, direction_zero_queue, confirm_queue, bridge_queue)
    produce_direction(1, direction_one_queue, confirm_queue, bridge_queue)

    get_cars_to_the_other_side(direction_zero_queue, direction_one_queue, confirm_queue, bridge_queue)
    terminate_finished_processes()

    print("Done")
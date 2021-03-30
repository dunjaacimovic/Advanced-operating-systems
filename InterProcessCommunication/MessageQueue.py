from multiprocessing import Queue, Process, active_children, current_process
from time import sleep, time
from queue import Empty
from random import uniform, randint

# Constants
DIRECTION_ZERO = 8
DIRECTION_ONE = 4
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


def get_cars_to_the_other_side(direction_zero_queue, direction_one_queue, confirm_queue, bridge_queue):
    first_direction = randint(0, 1)
    if first_direction == 0:
        start_with_zero(direction_zero_queue, direction_one_queue, confirm_queue, bridge_queue)
    else: 
        start_with_one(direction_zero_queue, direction_one_queue, confirm_queue, bridge_queue)

def start_with_zero(direction_zero_queue, direction_one_queue, confirm_queue, bridge_queue):
    while True:
        capacity = [BRIDGE_CAPACITY, BRIDGE_CAPACITY]
        capacity[0] = approve_and_cross("0", direction_zero_queue, confirm_queue, bridge_queue, capacity[0])
        capacity[1] = approve_and_cross("1", direction_one_queue, confirm_queue, bridge_queue, capacity[1])
        if capacity[0] == BRIDGE_CAPACITY and capacity[1] == BRIDGE_CAPACITY:
            print("\n------------------------------------------------\n\nTHERE IS NO MORE CARS.\n")
            break

def start_with_one(direction_zero_queue, direction_one_queue, confirm_queue, bridge_queue):
    while True:
        capacity = [BRIDGE_CAPACITY, BRIDGE_CAPACITY]
        capacity[1] = approve_and_cross("1", direction_one_queue, confirm_queue, bridge_queue, capacity[1])
        capacity[0] = approve_and_cross("0", direction_zero_queue, confirm_queue, bridge_queue, capacity[0])
        if capacity[0] == BRIDGE_CAPACITY and capacity[1] == BRIDGE_CAPACITY:
            print("\n------------------------------------------------\n\nTHERE IS NO MORE CARS.\n")
            break

    # while True:
    #     capacity = [BRIDGE_CAPACITY, BRIDGE_CAPACITY]
    #     if first_direction == 0:
    #         capacity[0] = approve_and_cross("0", direction_zero_queue, confirm_queue, bridge_queue, capacity[0])
    #         capacity[1] = approve_and_cross("1", direction_one_queue, confirm_queue, bridge_queue, capacity[1])
    #     else:
    #         capacity[1] = approve_and_cross("1", direction_one_queue, confirm_queue, bridge_queue, capacity[1])
    #         capacity[0] = approve_and_cross("0", direction_zero_queue, confirm_queue, bridge_queue, capacity[0])
    #     # print("\n\n----------------- Direction 1 -------------------")
    #     # # print("\nDirection 1")
    #     # capacity = [BRIDGE_CAPACITY, BRIDGE_CAPACITY]

    #     # while direction_one_queue.empty() and capacity[1] > 2:
    #     #     if handshake(direction_one_queue, confirm_queue):
    #     #         capacity[1] = capacity[1] - 1
    #     #     else:
    #     #         break

    #     # while direction_one_queue.empty() and capacity[1] > 1:
    #     #     if handshake(direction_one_queue, confirm_queue):
    #     #         capacity[1] = capacity[1] - 1
        
    #     # while direction_one_queue.empty() and capacity[1] > 0:
    #     #     if handshake(direction_one_queue, confirm_queue):
    #     #         capacity[1] = capacity[1] - 1
        
    #     # simulate_crossing(bridge_queue)
        
    #     # sleep(uniform(1.0, 3.0))
    #     # if not bridge_queue.empty():
    #     #     print("\nCars which crossed over are: ")
    #     #     while not bridge_queue.empty():
    #     #         message = bridge_queue.get()
    #     #         print("Bridge receives - " + message)
    #     # else:
    #     #     print("No cars have crossed in direction one.")

    #     # print("\n\n------------------ Direction 0 -------------------")
    #     # while direction_zero_queue.empty() and capacity[0] > 2:
    #     #     if handshake(direction_zero_queue, confirm_queue):
    #     #         capacity[0] = capacity[0] - 1
    #     #     else:
    #     #         break

    #     # while direction_zero_queue.empty() and capacity[0] > 1:
    #     #     if handshake(direction_zero_queue, confirm_queue):
    #     #         capacity[0] = capacity[0] - 1
        
    #     # while direction_zero_queue.empty() and capacity[0] > 0:
    #     #     if handshake(direction_zero_queue, confirm_queue):
    #     #         capacity[0] = capacity[0] - 1
        
    #     # simulate_crossing(bridge_queue)

    #     # sleep(uniform(1.0, 3.0))
    #     # if not bridge_queue.empty():
    #     #     print("\nCars which crossed over are: ")
    #     #     while not bridge_queue.empty():
    #     #         message = bridge_queue.get()
    #     #         print("Bridge receives - " + message)
    #     # else:
    #     #     print("No cars have crossed in direction zero.")

    #     if capacity[0] == BRIDGE_CAPACITY and capacity[1] == BRIDGE_CAPACITY:
    #         print("\n------------------------------------------------\n\nTHERE IS NO MORE CARS.\n")
    #         break

def approve_and_cross(direction, direction_queue, confirm_queue, bridge_queue, capacity):
    print("\n\n------------------ Direction " + direction + " -------------------")
    start_time = time()
    direction_time_limit = uniform(0.5, 1.0)
    # next_capacity = BRIDGE_CAPACITY
    # while time() - start_time < direction_time_limit:
    while direction_queue.empty() and capacity > 0 and time() - start_time < direction_time_limit:
        if handshake(direction_queue, confirm_queue):
            capacity = capacity - 1

    # while direction_queue.empty() and capacity > 2:
    #     if handshake(direction_queue, confirm_queue):
    #         capacity = capacity - 1

    # while direction_queue.empty() and capacity > 1:
    #     if handshake(direction_queue, confirm_queue):
    #         capacity = capacity - 1
    
    # while direction_queue.empty() and capacity > 0:
    #     if handshake(direction_queue, confirm_queue):
    #         capacity = capacity - 1

    simulate_crossing(bridge_queue)
    return capacity

# def approve_cars(capacity, direction_queue, confirm_queue):
#     start_time = time()
#     direction_time_limit = uniform(0.5, 1.0)
#     while capacity[0] > 0 and (time() - start_time) < direction_time_limit:
#         if handshake(direction_queue, confirm_queue):
#             capacity[0] -= 1
#         else:
#             break

def handshake(direction_queue, confirm_queue):
    message = "Bridge: a car can go over."
    print("\nBridge sends -", message)
    direction_queue.put(message)
    try:
        message = confirm_queue.get(timeout=(4.0))
        print("Bridge recieves -", message)
        return True
    except Empty:
        print("No more cars waiting in this direction.")
        return False 
        
def simulate_crossing(bridge_queue):
    sleep(uniform(1.0, 3.0))
    if not bridge_queue.empty():
        print("\nCars which crossed over are: ")
        while not bridge_queue.empty():
            message = bridge_queue.get()
            print("Bridge receives - " + message)
    else:
        print("No cars have crossed in this direction.")

    


def terminate_finished_processes():
    for child in active_children():
        child.join()
        print("Child process", str(child.pid), "joined.")      


if __name__ == '__main__':
    direction_zero_queue = Queue(1)
    direction_one_queue = Queue(1)
    confirm_queue = Queue(1)
    bridge_queue = Queue(BRIDGE_CAPACITY)

    produce_direction(0, direction_zero_queue, confirm_queue, bridge_queue)
    produce_direction(1, direction_one_queue, confirm_queue, bridge_queue)

    get_cars_to_the_other_side(direction_zero_queue, direction_one_queue, confirm_queue, bridge_queue)
    terminate_finished_processes()
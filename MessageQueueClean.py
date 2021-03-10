from multiprocessing import Queue, Process, active_children, current_process, freeze_support
from time import sleep
from queue import Empty

MISSIONARY_NUMBER = 3
CANNIBAL_NUMBER = 3
WAIT_ANCHORED = 4
BOAT_SEATS = 3
HANDSHAKE_TIME = (WAIT_ANCHORED / float(BOAT_SEATS + 4))


# - CREATE MISSIONARIES AND CANNIBALS -

def CreateMissionaries(missionary_queue, confirm_queue, boat_queue):
  for number in range(MISSIONARY_NUMBER):
    ID = str(number) + "M"
    missionary = Process(
        target=Travel, 
        args=(ID, "Missionary", missionary_queue, confirm_queue, boat_queue,)
    )
    missionary.start()

def CreateCannibals(cannibal_queue, confirm_queue, boat_queue):
  for number in range(CANNIBAL_NUMBER):
    ID = str(number) + "C"
    missionary = Process(
        target=Travel, 
        args=(ID, "Cannibal", cannibal_queue, confirm_queue, boat_queue,)
    )
    missionary.start()

def Travel(ID, passenger_kind, passenger_queue, confirm_queue, boat_queue):
  message = passenger_queue.get()
  print(ID + " receives - " + message)

  message = ID + ": " + passenger_kind + " embarked."
  print(ID + " sends - " + passenger_kind + " embarked.")
  confirm_queue.put(message)

  message = ID + ": " + passenger_kind + " passenger."
  print(ID + " sends - " + passenger_kind + " passenger.")
  boat_queue.put(message)
    

# - TRANSPORT -

def TransportPassengers(missionary_queue, cannibal_queue, confirm_queue, boat_queue):
  while (True):
    seats_empty = [BOAT_SEATS]

    while missionary_queue.empty() and cannibal_queue.empty() and seats_empty[0] >= 2:
      if (Handshake("missionary", missionary_queue, confirm_queue)):
        seats_empty[0] = seats_empty[0] - 1
      else:
        break

      if (Handshake("cannibal", cannibal_queue, confirm_queue)):
        seats_empty[0] = seats_empty[0] - 1
      else:
        break
    #Possible states after mixed embarking: a)M = C, b)M = C+1, c)C = M+1
    
    while missionary_queue.empty() and seats_empty[0] >= 1:
      if (Handshake("missionary", missionary_queue, confirm_queue)):
        seats_empty[0] = seats_empty[0] - 1
    
    if (seats_empty[0] >= (BOAT_SEATS - 1)):
      while cannibal_queue.empty() and seats_empty[0] >= 1:
        if (Handshake("cannibal", cannibal_queue, confirm_queue)):
          seats_empty[0] = seats_empty[0] - 1
    
    sleep(2 * HANDSHAKE_TIME)
    print("--- Passenger manifest ---")
    while (not boat_queue.empty()):
      message = boat_queue.get()
      print("Boat" + " receives - " + message)
    print("---                    ---")

    if (seats_empty[0] == BOAT_SEATS):
      print("There are no passengers waiting to be rowed across.")
      break
    print("")

def Handshake(passenger_kind, passenger_queue, confirm_queue):
  message = "Boat" + ": " + "A " + passenger_kind + " can embark."
  print("Boat" + " sends - " + "A " + passenger_kind + " can embark.")
  passenger_queue.put(message)
  try:
    message = confirm_queue.get(timeout=HANDSHAKE_TIME)
    print("Boat" + " receives - " + message)
    return True
  except Empty:
    return False


def TerminateFinishedProcesses():
  for child_process in active_children():
    pid = str(child_process.pid)
    child_process.join()
    print("Process " + pid + " joined.")
  
if __name__ == '__main__':  
  missionary_queue = Queue(1)
  cannibal_queue = Queue(1)
  confirm_queue = Queue(1)
  boat_queue = Queue(BOAT_SEATS)
  
  CreateMissionaries(missionary_queue, confirm_queue, boat_queue)
  CreateCannibals(cannibal_queue, confirm_queue, boat_queue)

  TransportPassengers(missionary_queue, cannibal_queue, confirm_queue, boat_queue)
  TerminateFinishedProcesses()
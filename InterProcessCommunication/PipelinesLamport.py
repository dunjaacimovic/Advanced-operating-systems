import multiprocessing 
from ctypes import Structure, c_int
from enum import Enum
from time import sleep
from heapq import heappush, heappop
from random import randint

TIMEOUT = 1.0/3.0
SIZE_OF_DATABASE = 10

class Message(Enum):
    request = "REQUEST"
    reply = "REPLY"
    release = "RELEASE"

class DBEntryStruct(Structure):
    _fields_ = [('id', c_int), ('clock', c_int), ('cs_entries', c_int)]

class DBEntry:
    def __init__(self, ID, pipes):
        self.ID = ID
        self.pipes = pipes
        self.clock = 0
        self.request_queue = []
        self.replies = []

    def receive_messages(self):
        for pipe in self.pipes:
            if pipe != False and pipe.poll(TIMEOUT):
                message = pipe.recv()
                self.act_on_message(message)

    def act_on_message(self, message):
        time_stamp, text, sender_ID = message
        self.say("Received " + text + " from " + str(sender_ID))

        #syncronise clock
        if time_stamp >= self.clock:
            self.clock = time_stamp + 1
        else:
            self.clock += 1

        #handle message
        if(text == Message.request.value):
            #add request to queue
            heappush(self.request_queue, message)
            #reply to sender
            reply = [self.clock, Message.reply.value, self.ID]
            self.say("Sending " + Message.reply.value + " to " + str(sender_ID))
            self.pipes[sender_ID].send(reply)
        elif(text == Message.release.value):
            removed_request = heappop(self.request_queue) 
        elif(text == Message.reply.value):
            self.replies.append(message)

    def say(self, text):
        print(self.ID * "\t" + str(self.ID) + "[" + str(self.clock) + "]: " + text)


    def send_request(self):
        request = (self.clock, Message.request.value, self.ID)
        #add request to queue
        heappush(self.request_queue, request)
        #send request to all
        self.say("Sending " + Message.request.value + " to all")
        for pipe in self.pipes:
            if pipe != False: pipe.send(request)

    def wait_for_your_turn_to_eat(self):
        while not (self.request_queue[0][2] == self.ID and len(self.replies) == (SIZE_OF_DATABASE - 1)):
            self.receive_messages()
        print(len(self.replies))

    def delete_replies(self):
        self.replies = []
    
    def send_release(self):
        message = heappop(self.request_queue)
        release = (message[0], Message.release.value, self.ID)
        #send request to all
        self.say("Sending " + Message.release.value + " to all")
        for pipe in self.pipes:
            if pipe != False: pipe.send(release)


def work(ID, pipes, database):
    db_entry = DBEntry(ID, pipes)
    for _ in range(5):
        db_entry.receive_messages()
        enter_database(db_entry, database)
        # db_entry.receive_messages()

def enter_database(db_entry, database):
    db_entry.send_request()
    db_entry.wait_for_your_turn_to_eat()
    db_entry.delete_replies()
    db_entry.say("--- Writing ---")
    sleep(20)
    db_entry.say("... Done writing ...")
    sleep(1)
    db_entry.send_release()

def wait_until_they_all_finish():
    active_processes = multiprocessing.active_children()
    while (active_processes):
        print("Sleeping until they finish philosophizing...")
        sleep(10)
        active_processes = multiprocessing.active_children()


if __name__ == '__main__':

    multiprocessing.freeze_support()
    #create database
    # n = randint(3, 10)
    n = 10
    database = multiprocessing.Array(DBEntryStruct, [(i, 0, 0) for i in range(n)])

    #create pipe matrix 
    pipe_matrix = [[False for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for column in range(row + 1, n):
            pipe_matrix[row][column], pipe_matrix[column][row] = multiprocessing.Pipe()
        
    print("Done with pipe-matrix.")
    #create and start processes
    for i in range(n):
        entry = multiprocessing.Process(target=work, args=(i, pipe_matrix[i], database,))
        entry.start()
    print("Started all processes")
    
    wait_until_they_all_finish()





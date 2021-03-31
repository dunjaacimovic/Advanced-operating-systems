import multiprocessing 
from ctypes import Structure, c_int, c_bool
from enum import Enum
from time import sleep
from heapq import heappush, heappop
from random import randint, uniform
from functools import reduce

TIMEOUT = 1.0/3.0
NUMBER_OF_ENTRIES = 5

class Message(Enum):
    REQUEST = "REQUEST"
    REPLY = "REPLY"

class DBEntryStruct(Structure):
    _fields_ = [('id', c_int), ('clock', c_int), ('cs_entries', c_int)]

class DBEntry:
    def __init__(self, ID, pipes):
        self.ID = ID
        self.pipes = pipes
        self.clock = 0
        self.cs_entries = 0
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
        self.clock = time_stamp + 1 if time_stamp >= self.clock else self.clock + 1
        if text == Message.REQUEST.value:
            heappush(self.request_queue, message)
            if self.request_queue[0][2] != self.ID:
                heappop(self.request_queue)
                reply = [self.clock, Message.REPLY.value, self.ID]
                self.say("Sending " + Message.REPLY.value + " to " + str(sender_ID))
                self.pipes[sender_ID].send(reply)
        elif text == Message.REPLY.value:
            self.replies.append(message)
    
    def say(self, text, database=False):
        if database:
            print(self.ID * 4 * "\t" + text)
        else:
            print(self.ID * 4 * "\t" + str(self.ID) + "[" + str(self.clock) + "]: " + text)

    def send_request(self):
        request = (self.clock, Message.REQUEST.value, self.ID)
        heappush(self.request_queue, request)
        self.say("Sending " + Message.REQUEST.value + " to all") 
        for pipe in self.pipes:
            if pipe != False: pipe.send(request)
    
    def wait_for_your_turn(self):
        while not len(self.replies) == len(self.pipes) - 1:
            self.receive_messages()

    def delete_replies(self):
        self.replies = []

    def send_delayed_replies(self):
        heappop(self.request_queue)
        while(True):
            try:
                request_clock, text, sender_ID = heappop(self.request_queue)
                reply = [self.clock, Message.REPLY.value, self.ID]
                self.say("Sending " + Message.REPLY.value + " to " + str(sender_ID))
                self.pipes[sender_ID].send(reply) 
            except IndexError:
                break
    def update_structure(self):
        self.cs_entries += 1
        return DBEntryStruct(self.ID, self.clock, self.cs_entries)
        
def work(ID, pipes, database, active_entries):
    db_entry = DBEntry(ID, pipes)
    for _ in range(NUMBER_OF_ENTRIES):
        db_entry.receive_messages()
        db_entry.send_request()
        db_entry.wait_for_your_turn()
        enter_database(db_entry, database, active_entries)
        db_entry.send_delayed_replies()
    
    while(active_entries.value):
        db_entry.receive_messages()


def enter_database(db_entry, database, active_entries):
    db_entry.delete_replies()
    db_entry.say("--- DATABASE ---", database=True)
    database[db_entry.ID] = db_entry.update_structure()
    for entry in database:
        db_entry.say("[ID: " + str(entry.id) + " - C: " + str(entry.clock) + " - E: " + str(entry.cs_entries) + "]", database=True)
    active_entries.value = reduce(lambda num1, num2: num1 + num2, [1 if e.cs_entries == NUMBER_OF_ENTRIES else 0 for e in database]) != len(database)
    db_entry.say("................", database=True)
    sleep(uniform(0.1, 2))

def wait_until_they_all_finish():
    active_process = multiprocessing.active_children()
    while(active_process):
        sleep(10)
        active_process = multiprocessing.active_children()
        

if __name__ == '__main__':
    #create database
    n = randint(3, 8)
    database = multiprocessing.Array(DBEntryStruct, [(i, 0, 0) for i in range(n)])
    active_entries = multiprocessing.Value(c_bool, True)

    #create pipe matrix 
    pipe_matrix = [[False for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for column in range(row+1, n):
            pipe_matrix[row][column], pipe_matrix[column][row] = multiprocessing.Pipe()
    for i in range(n):
        entry = multiprocessing.Process(target=work, args=(i, pipe_matrix[i], database, active_entries))
        entry.start()
    wait_until_they_all_finish()
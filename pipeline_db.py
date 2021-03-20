from multiprocessing import Process, Pipe, active_children
from random import uniform, randint
from time import sleep

database = []

class DBEntry:

    def __init__(self, id, logical_clock, cs_entries):
        self.id = id
        self.logical_clock = logical_clock
        self.cs_entries = cs_entries

    def update(self, logical_clock_update):
        self.logical_clock = logical_clock_update
        self.cs_entries += 1

    def __str__(self):
        return "ID: " + str(self.id) + " - LCLOCK: " + str(self.logical_clock) + " - CS ENTRIES: " + str(self.cs_entries)
    
    def __repr__(self):
        return "ID: " + str(self.id) + " - LCLOCK: " + str(self.logical_clock) + " - CS ENTRIES: " + str(self.cs_entries)
    
    
def critical_section(conn, i, logical_clock):
    print(i, logical_clock)
    # database[i].update(logical_clock)
    for db_entry in database: 
        print(db_entry)
    # sleep(uniform(0.1, 2.0))
    conn.send("All done w/ critical section")
    conn.close()
    

# def f(conn):
#     conn.send("hello from critical section")
#     conn.close()

if __name__ == '__main__':
    for id in range(randint(3, 10)):
        database.append(DBEntry(id, 0, 0))
    
    # critical_section(1, 1)
    parent_conn, child_conn = Pipe()
    p = Process(target=critical_section, args=(child_conn, 1, 1))
    p.start()
    print(parent_conn.recv())   # prints "[42, None, 'hello']"
    p.join()
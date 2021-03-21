from ctypes import Structure, c_int
from random import randint, uniform
from time import sleep
import multiprocessing

class DBEntry(Structure):
    _fields_ = [('id', c_int), ('logical_clock', c_int), ('cs_entries', c_int)]

def work_with_database(database, conn, i, logical_clock):
    request = (database[i].logical_clock, "REQUEST", database[i].id)
    # critical_section(database, conn, i, logical_clock)

def critical_section(database, conn, i, logical_clock):
    print(i, logical_clock)
    database[i].logical_clock = logical_clock
    database[i].cs_entries += 1

    # Printing 
    print("Database (in process):")
    for entry in database:
        print(entry.id, entry.logical_clock, entry.cs_entries)
    sleep(uniform(0.1, 2.0))
    
    conn.send("All done w/ critical section")
    conn.close()

if __name__ == '__main__':

    # create database
    n = randint(3, 10)
    database = multiprocessing.Array(DBEntry, [(i, 0, 0) for i in range(n)])
    
    # create pipe matrix 
    matrix = [[False for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for column in range(row + 1, n):
            matrix[row][column], matrix[column][row] = multiprocessing.Pipe()

    # create processes
    processes = []
    for i in range(n):
        processes.append(multiprocessing.Process(target=work_with_database, args=(database, pipe_matrix[i])))
        processes[i].start()

    for i in range(n):
        processes[i].join()

    # p = multiprocessing.Process(target=critical_section, args=(database, child_conn, 1, 1))
    # p.start()
    # print(parent_conn.recv())   # prints ""All done w/ critical section""
    # p.join()

    # Printing
    print("Database (in main program): ")
    for entry in database:
        print(entry.id, entry.logical_clock, entry.cs_entries)


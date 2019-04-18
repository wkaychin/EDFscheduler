# Wanqi Chin
# Suleyman Yusupov
# EDF and RM Scheduler

from operator import attrgetter
import sys
import time


class Tasks(object):
    taskcount = 0

    def __init__(self, name, period, wcex18, wcex19, wcex64, wcex38, ex_time):
        self.name = name
        self.period = period
        self.wcex18 = wcex18
        self.wcex19 = wcex19
        self.wcex64 = wcex64
        self.wcex38 = wcex38
        self.ex_time = ex_time

    def display_task(self):
        print("Name:", self.name, ",period:", self.period, "wcex18: ", self.wcex18, "wcex19: ", self.wcex19, "wcex64: ",
              self.wcex64, "wcex38: ", self.wcex38, "ex_time: ", self.ex_time)

    def __getitem__(self, period):
        return self.period


def fileorganizer():
    # algorithm = sys.argv[2]
    f = open(sys.argv[1], "r")
    textfile = f.read()
    f.close()
    i = 0
    j = 0
    splittasks = textfile.splitlines()
    header = splittasks[0].split()
    pretasks = []
    tasks = []
    for x in splittasks:
        if (i == 0):
            i = i + 1
        else:
            pretasks.append(x.split())
            i = i + 1

    print(pretasks[0][0])
    for x in pretasks:
        tasks.append(Tasks(x[0], x[1], x[2], x[3], x[4], x[5], 0))

    return tasks


def rmscheduler(tasklist):
    file = open("rmschedule.txt", "w")
    # organize the tasks in the RM order
    timer = 1
    # for x in tasklist:
    #   x.display_task()
    stop = 0

    sortedtasks = sorted(tasklist, key=lambda task: task.period)
    # for x in sortedtasks:
    #    x.display_task()

    while (timer < 1000):
        backtowhile = 0
        ready = edfreadytasks(sortedtasks, timer)
        if (timer == 1):
            print("@ 1188 Mhz")
        if (timer >= 1000):
            break
        if (stop == 1):
            break
        ready = sorted(ready, key=lambda task: task.period)
        for idx, x in enumerate(ready):
            if (stop == 1):
                break
            if (backtowhile == 1):
                break
            ready = edfreadytasks(ready, timer)
            ready = sorted(ready, key=lambda task: task.period)

            for idn, n in enumerate(sortedtasks):
                if (int(n.period) * (n.ex_time) >= (timer + int(x.wcex18))):
                    backtowhile = 1
                    break
            print_string = (timer, x.name, timer + int(x.wcex18), str(0.625 * int(x.wcex18)) + "J")
            sortedtasks[idx].ex_time = int(sortedtasks[idx].ex_time) + 1
            x.ex_time = int(x.ex_time) + 1
            file.write(str(print_string) + "\n")

            for k in sortedtasks:
                if ((int(k.period)) * (x.ex_time) < (timer + int(k.wcex18))):
                    print_miss = ("Period Missed by " + k.name)
                    file.write(str(print_miss) + "\n")
                    stop = 1
                    break

            if (timer + int(x.wcex18) >= 1000):
                break
            timer = timer + int(x.wcex18) + 1
        if (timer < 1000) and (not ready):
            idle_string = ("IDLE " + "elapsed time is: " + str(timer))
            file.write(str(idle_string) + "\n")
            timer = timer + 5
        if (timer >= 1000):
            break

    file.close()


def edfscheduler(tasks):
    file = open("edfschedule.txt", "w")
    print("EDF Schedule @ 1188 MHz")
    timer = 0
    # ready = edfreadytasks()
    time_elapsed =0
    while (time_elapsed < 1000):
        ready = edfreadytasks(tasks, timer)  # list of ready tasks
        ready = sorted(ready, key=lambda task: task.period)  # not neccessary but sorts the ready list by task period
        for idx, x in enumerate(ready):
            ready = edfreadytasks(ready, timer)
            ready = sorted(ready, key=lambda task: task.period)
            # for t in ready: print(t.name)
            print_string = (timer, x.name, timer + int(x.wcex18), str(0.625 * int(x.wcex18)) + "J")
            file.write(str(print_string) + "\n")
            if (int(x.period) * x.ex_time) > timer + int(x.wcex38) * x.ex_time:
                file.write("Deadline Missed")
                break
            x.ex_time = int(x.ex_time) + 1
            timer = timer + int(x.wcex18)
            time_elapsed = timer + int(x.wcex18) + 1
        if (time_elapsed < 1000) and (not ready):
            idle_string = ("IDLE " + "elapsed time is: " + str(time_elapsed))
            file.write(str(idle_string) + "\n")
            time_elapsed = time_elapsed + 5
    file.close()


def edfreadytasks(tasks, timer):
    ready = []
    for x in tasks:
        if timer >= (int(x.period) * x.ex_time):
            ready.append(x)
    return ready


def eefinder(task):
    temp = task.wcex18, task.wcex19, task.wcex64, task.wcex38

    ec = int(temp[0]) * 0.625, int(temp[1]) * 0.447, int(temp[2]) * 0.307, int(temp[3]) * 0.212
    if (ec[0] < ec[1] and ec[0] < ec[2] and ec[0] < ec[3]):

        return 1
    elif (ec[1] < ec[0] and ec[1] < ec[2] and ec[1] < ec[3]):

        return 2
    elif (ec[2] < ec[0] and ec[2] < ec[1] and ec[2] < ec[3]):

        return 3
    elif (ec[3] < ec[0] and ec[3] < ec[1] and ec[3] < ec[2]):

        return 4


def rmee(tasklist):
    timer = 1
    sortedtasks = sorted(tasklist, key=lambda task: task.period)
    for x in sortedtasks:
        i = eefinder(x)
        if (i == 1):
            print(timer, x.name, timer + int(x.wcex18), str(0.625 * int(x.wcex18)) + "J")
            if (int(x.period) < timer + int(x.wcex18)):
                print("Period Missed")
            timer = timer + int(x.wcex18) + 1
        elif (i == 2):
            print(timer, x.name, timer + int(x.wcex19), str(0.447 * int(x.wcex19)) + "J")
            if (int(x.period) < timer + int(x.wcex19)):
                print("Period Missed")
            timer = timer + int(x.wcex19) + 1
        elif (i == 3):
            print(timer, x.name, timer + int(x.wcex64), str(0.307 * int(x.wcex64)) + "J")
            if (int(x.period) < timer + int(x.wcex64)):
                print("Period Missed")
            timer = timer + int(x.wcex64) + 1
        elif (i == 4):
            print(timer, x.name, timer + int(x.wcex38), str(0.212 * int(x.wcex38)) + "J")
            if (int(x.period) < timer + int(x.wcex38)):
                print("Period Missed")
            timer = timer + int(x.wcex38) + 1


def ee_edfscheduler(tasks):
    file = open("edfschedule.txt", "w")
    # file = open("edfschedule.txt", "w")
    print("EDF Schedule @ 1188 MHz")
    timer = 0
    # ready = edfreadytasks()
    time_elapsed = 0
    while (time_elapsed < 1000):
        ready = edfreadytasks(tasks, timer)  # list of ready tasks
        ready = sorted(ready, key=lambda task: task.period)  # not neccessary but sorts the ready list by task period
        for idx, x in enumerate(ready):
            # i = eefinder(x)
            ready = edfreadytasks(ready, timer)
            ready = sorted(ready, key=lambda task: task.period)
            i = eefinder(x)
            if (i == 1):
                print_string = (timer, x.name, timer + int(x.wcex18), str(0.625 * int(x.wcex18)) + "J")
                file.write(str(print_string) + "\n")
                timer = timer + int(x.wcex18)

                time_elapsed = timer + time_elapsed + 1
                x.ex_time = int(x.ex_time) + 1
            elif (i == 2):
                print_string = (timer, x.name, timer + int(x.wcex19), str(0.447 * int(x.wcex19)) + "J")
                file.write(str(print_string) + "\n")
                timer = timer + int(x.wcex19)

                time_elapsed = timer + time_elapsed + 1
                x.ex_time = int(x.ex_time) + 1
            elif (i == 3):
                print_string = (timer, x.name, timer + int(x.wcex64), str(0.307 * int(x.wcex64)) + "J")
                file.write(str(print_string) + "\n")
                timer = timer + int(x.wcex64)

                time_elapsed = timer + time_elapsed + 1
                x.ex_time = int(x.ex_time) + 1
            elif (i == 4):
                print_string = (timer, x.name, timer + int(x.wcex38), str(0.212 * int(x.wcex38)) + "J")
                file.write(str(print_string) + "\n")
                timer = timer + int(x.wcex38)

                time_elapsed = timer + time_elapsed + 1
                x.ex_time = int(x.ex_time) + 1
            if (time_elapsed < 1000) and (not ready):
                idle_string = ("IDLE " + "elapsed time is: " + str(time_elapsed))
                print(idle_string)
                file.write(str(idle_string) + "\n")
                time_elapsed = time_elapsed + 5
        file.close()

rm = ("RM")
edf = ("EDF")
ee = ("EE")
a = fileorganizer()

if len(sys.argv) == 3:
    if (sys.argv[2] == rm):
        rmscheduler(a)
    elif (sys.argv[2] == edf):
        edfscheduler(a)
elif len(sys.argv) == 4:
    if (sys.argv[2] == rm and (sys.argv[3]) == ee):
        rmee(a)
    elif (sys.argv[2] == edf and (sys.argv[3]) == ee):
        ee_edfscheduler(a)

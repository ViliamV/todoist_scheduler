#!/usr/bin/env python3
from pytodoist import todoist
import os
from datetime import timedelta
from datetime import date
from task_class import *
import argparse

parser = argparse.ArgumentParser(description='''Todoist Scheduler can store future one-time or recurring tasks for Todoist \n
                                                in plaintext and create a task in Todoist when they are needed. \n
                                                Also offers more features regarding a set of repeating tasks.''')
parser.add_argument('-f', dest='frontload', type=int, default=0,
                        help='Useful when you are going to be away from computer for X days. Use X as a parameter.')
frontload = parser.parse_args().frontload                        
directory = os.path.dirname(os.path.realpath(__file__))
with open(directory + '/login', 'r') as f:
    login, password = f.read().strip().split(' ')
user = todoist.login(login, password)
one_time_dir, recurring_dir = None, None
with open(directory + '/todoist_scheduler.conf') as conf:
    for line in conf:
        if line[0] == 'O':
            one_time_dir = line[2:].strip()
        elif line[0] == 'R':
            recurring_dir = line[2:].strip()
if one_time_dir is not None:
    print('One time tasks:')
    for p in os.listdir(one_time_dir):
        print('Dealing with task {}.'.format(p))
        task = OneTime(one_time_dir + '/' + p)
        if task.execute(user, frontload=frontload):
            task.delete_file()
        print()
if recurring_dir is not None:
    print('Recurring tasks:')
    for p in os.listdir(recurring_dir):
        print('Dealing with task {}.'.format(p))
        task = Recurring(recurring_dir + '/' + p)
        if task.execute(user, frontload=frontload):
            task.write_task()
        print()

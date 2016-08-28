#!/usr/bin/env python3
from pytodoist import todoist
import os
from datetime import timedelta
from datetime import date
from task_class import *
import argparse
import pickle

parser = argparse.ArgumentParser(description='''Todoist Scheduler can store future one-time or recurring tasks for Todoist \n
                                                in plaintext and create a task in Todoist when they are needed. \n
                                                Also offers more features regarding a set of repeating tasks.''')
parser.add_argument('-f', dest='frontload', type=int, default=0,
                        help='Useful when you are going to be away from computer for X days. Use X as a parameter.')
parser.add_argument('-v', dest='verbose', action='store_true',
                        help='Verbose output.')
parser.add_argument('--first', dest='first_start', action='store_true',
                        help='First start of a script. Creates login information file and default config.')
    
frontload = parser.parse_args().frontload  
verbose = parser.parse_args().verbose  
directory = os.path.dirname(os.path.realpath(__file__))                    
if parser.parse_args().first_start:
    working_login = False
    print('This is a Todoist Scheduler. First input your Todoist login information.')
    while not working_login:   
        login = input('Login: ')
        password = input('Password: ')        
        #login, password = pickle.load(open('login', 'rb'))
        #print(login, password)
        #test connection
        try:
            user = todoist.login(login, password)
            working_login = True
            print('Login successful. The credentials are stored in working directory in file \'login\'.')
        except:
            print('Login unsuccessful. Try again, please.')
    pickle.dump((login, password), open(directory + '/login', 'wb'))
    one_time_dir = directory + '/one_time'
    recurring_dir = directory + '/recurring'
    if not os.path.exists(one_time_dir):
        os.makedirs(one_time_dir)
    if not os.path.exists(recurring_dir):
        os.makedirs(recurring_dir)
    print('Creating default configuration file todoist_scheduler.conf.  Feel free to change it.')
    with open(directory + '/todoist_scheduler.conf', 'w') as f:
        f.write('# Directory for One time tasks:\n')
        f.write('O {}\n'.format(one_time_dir))
        f.write('# Directory for Recurring tasks:\n')
        f.write('R {}\n'.format(recurring_dir))
        f.write('# You can change the directories as you like.')
    print('By default, one-time tasks will be stored in directory\n {} and recurring tasks in directory\n {}.'.format(one_time_dir, recurring_dir))
# normal run
login, password = pickle.load(open('login', 'rb'))
user = todoist.login(login, password)
one_time_dir, recurring_dir = None, None
with open(directory + '/todoist_scheduler.conf') as conf:
    for line in conf:
        if line[0] == 'O':
            one_time_dir = line[2:].strip()
        elif line[0] == 'R':
            recurring_dir = line[2:].strip()
if one_time_dir is not None:
    if verbose: print('One time tasks:')
    for p in os.listdir(one_time_dir):
        if verbose: print('Dealing with task {}.'.format(p))
        task = OneTime(one_time_dir + '/' + p)
        if task.execute(user, verbose, frontload=frontload):
            task.delete_file(verbose)
        if verbose: print()
if recurring_dir is not None:
    if verbose: print('Recurring tasks:')
    for p in os.listdir(recurring_dir):
        if verbose: print('Dealing with task {}.'.format(p))
        task = Recurring(recurring_dir + '/' + p)
        if task.execute(user, verbose, frontload=frontload):
            task.write_task(verbose)
        if verbose: print()

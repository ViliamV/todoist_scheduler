#!/usr/bin/env python3
from pytodoist import todoist
import os
from task import *
import argparse
import pickle
import toml

parser = argparse.ArgumentParser(description='''Todoist Scheduler can store future one-time or recurring tasks for Todoist \n
                                                in plain text and create a task in Todoist when they are needed. \n
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
    print('This is a Todoist Scheduler. Please enter your Todoist email and password.')
    print('They will be stored unencrypted as Python Pickle file so do not share the file \'login\'')
    while not working_login:
        email = input('Email: ')
        password = input('Password: ')
        try:
            todoist.login(email, password)
            working_login = True
            print('Login successful.')
        except:
            print('Login unsuccessful. Please, try again.')
    pickle.dump((email, password), open(directory + '/login', 'wb'))
    dir = directory + '/tasks'
    if not os.path.exists(dir):
        os.makedirs(dir)
    print('Creating default configuration file todoist_scheduler.conf.  Feel free to change it.')
    conf = {"login": directory + '/login', "tasks_directory": dir}
    toml.dump(conf, open(f'{directory}/todoist_scheduler.conf', 'w'))
    print('By default, tasks will be stored in directory:\n{}.'.format(dir))
    exit()
# normal run
# load conf

conf = toml.load(f'{directory}/todoist_scheduler.conf')
user = todoist.login(*pickle.load(open(conf['login'], 'rb')))
for f in os.listdir(conf['tasks_directory']):
    if '.toml' in f or '.TOML' in f:
        if verbose: print('Dealing with task "{}".'.format(f.split('.')[0]))
        filename = "{}/{}".format(conf['tasks_directory'], f)
        with open(filename) as ff:
            task = from_file(filename)
            execute(task, user, verbose, filename, frontload)

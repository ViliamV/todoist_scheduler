#!/usr/bin/env python3
from pytodoist import todoist
import os
from task import from_file, execute_task
from template import execute_template
import argparse
import pickle
import toml

parser = argparse.ArgumentParser(
    description="""Todoist Scheduler can store future one-time or recurring tasks for Todoist \n
                                                in plain text and create a task in Todoist when they are needed. \n
                                                Also offers more features regarding a set of repeating tasks."""
)
parser.add_argument(
    "-f",
    dest="frontload",
    type=int,
    default=0,
    help="Useful when you are going to be away from computer for X days. Use X as a parameter.",
)
parser.add_argument("-v", dest="verbose", action="store_true", help="Verbose output.")
parser.add_argument(
    "--first",
    dest="first_start",
    action="store_true",
    help="First start of a script. Creates login information file and default config.",
)
parser.add_argument('--template', help='Run template file TEMPLATE')
parser.add_argument('--date', help='due date for project created from TEMPLATE')

args = parser.parse_args()
frontload = args.frontload
verbose = args.verbose
directory = os.path.dirname(os.path.realpath(__file__))
first_start = args.first_start
template = args.template
due_date = args.date

if first_start:
    working_login = False
    print("This is a Todoist Scheduler. Please enter your Todoist email and password.")
    print(
        "They will be stored unencrypted as Python Pickle file so do not share the file 'login'"
    )
    while not working_login:
        email = input("Email: ")
        password = input("Password: ")
        try:
            todoist.login(email, password)
            working_login = True
            print("Login successful.")
        except:
            print("Login unsuccessful. Please, try again.")
    pickle.dump((email, password), open(directory + "/login", "wb"))
    dirs = [directory + "/tasks", directory + "/templates"]
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)
    print(
        "Creating default configuration file todoist_scheduler.conf.  Feel free to change it."
    )
    conf = {"login": directory + "/login", "tasks_directory": dirs[0], "templates_directory": dirs[1]}
    toml.dump(conf, open(f"{directory}/todoist_scheduler.conf", "w"))
    print("By default, tasks will be stored in directory:\n{}.".format(dir))
    exit()

else:
    conf = toml.load(f"{directory}/todoist_scheduler.conf")
    try:
        user = todoist.login(*pickle.load(open(conf["login"], "rb")))
    except:
        try:
            from gi.repository import Notify

            Notify.init("Todoist scheduler")
            notification = Notify.Notification.new("Unable to log in Todoist")
            notification.set_urgency(2)
            notification.show()
        except:
            pass
        finally:
            exit()
    if template:
        execute_template(template, user, due_date)
    else:
        for dirpath, dirs, files in os.walk(conf["tasks_directory"]):
            for f in files:
                if ".toml" in f.lower():
                    if verbose:
                        print(f'Dealing with task "{f}".')
                    filename = f'{dirpath}/{f}'
                    with open(filename) as ff:
                        task = from_file(filename)
                        execute(task, user, verbose, filename, frontload)

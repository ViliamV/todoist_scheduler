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
parser.add_argument('--template', help='Run template file TEMPLATE')

args = parser.parse_args()
frontload = args.frontload
verbose = args.verbose
template = args.template
directory = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    if os.path.isfile(f"{directory}/todoist_scheduler.conf"):
        conf = toml.load(f"{directory}/todoist_scheduler.conf")
    else:
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
        dir = directory + "/tasks"
        if not os.path.exists(dir):
            os.makedirs(dir)
        print(
            "Creating default configuration file todoist_scheduler.conf"
        )
        conf = {"login": directory + "/login", "tasks_directory": dir}
        toml.dump(conf, open(f"{directory}/todoist_scheduler.conf", "w"))
        print("By default, tasks will be stored in directory:\n{}.".format(dir))
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
            exit(1)
    if template:
        execute_template(template, user)
    else:
        for dirpath, dirs, files in os.walk(conf["tasks_directory"]):
            if verbose:
                print(f'Directory: {os.path.relpath(dirpath, conf["tasks_directory"])}')
            for f in files:
                if ".toml" in f.lower():
                    if verbose:
                        print(f'  Task: {f}')
                    filename = f'{dirpath}/{f}'
                    with open(filename) as ff:
                        task = from_file(filename)
                        execute_task(task, user, verbose, filename, frontload)

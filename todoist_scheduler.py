#!/usr/bin/env python3
import os
from task import from_file, execute_task
from template import execute_template
from api import API
import argparse
import pickle
import toml

parser = argparse.ArgumentParser(
    description="""Todoist Scheduler can store future one-time or recurring tasks for Todoist \n
                   in plain text and create a task in Todoist when they are needed. \n
                   Also offers more features regarding a set of repeating tasks."""
)
parser.add_argument(
    "-f", dest="forward", type=int, default=0, help="Execute tasks due in next X days."
)
parser.add_argument("-v", dest="verbose", action="store_true", help="Verbose output.")
parser.add_argument("--template", help="Run template file TEMPLATE")

args = parser.parse_args()
directory = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    if os.path.isfile("{}/todoist_scheduler.conf".format(directory)):
        conf = toml.load("{}/todoist_scheduler.conf".format(directory))
        token_location = conf.get("token")
        token = pickle.load(open(token_location, "rb"))
        api = API(token)
    else:
        api = API.create_new(directory)
    if api.valid:
        if args.template:
            execute_template(args.template, api)
        else:
            for dirpath, dirs, files in os.walk(conf["tasks_directory"]):
                if args.verbose:
                    print(
                        "Directory: {}".format(
                            os.path.relpath(dirpath, conf["tasks_directory"])
                        )
                    )
                for f in files:
                    if ".toml" in f.lower():
                        if args.verbose:
                            print("  Task: {}".format(f))
                        filename = "{}/{}".format(dirpath, f)
                        with open(filename) as ff:
                            task = from_file(filename)
                            execute_task(task, api, args.verbose, filename, args.forward)
    else:
        print("Token not valid")
        exit(1)

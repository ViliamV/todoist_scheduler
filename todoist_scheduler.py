#!/usr/bin/env python3
from task import Task
import pathlib
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
directory = pathlib.Path(__file__).resolve().parent

if __name__ == "__main__":
    conf_file = directory / "todoist_scheduler.conf"
    if not conf_file.is_file():
        api = API.create_new(directory, missing_conf=True)
    else:
        conf = toml.load(str(conf_file))
        token_location = conf.get("token")
        if not token_location:
            api = API.create_new(directory, missing_location=True)
        else:
            token = pickle.load(open(token_location, "rb"))
            if not token:
                api = API.create_new(directory, missing_token=True)
            else:
                api = API(token)
    if api.valid:
        if args.template:
            execute_template(args.template, api)
        else:
            tasks = pathlib.Path(conf["tasks_directory"])
            for filename in tasks.rglob("*.toml"):
                if args.verbose:
                    print("Task: {}".format(filename.name))
                task = Task.from_file(filename, api, args.verbose)
                task.execute(args.forward)
    else:
        print("Token not valid")
        exit(1)

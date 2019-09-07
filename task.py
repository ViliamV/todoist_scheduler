import toml
import os
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from datetime import datetime, date

default = {
    "project": None,
    "tasks": None,
    "due_date": None,
    "early": None,
    "interval": None,
    "repeat": None,
    "repeat_index": None,
    "index": None,
    "priority": 2,
}


def string_to_relativedelta(s, num_pos=0, text_pos=1):
    if s is None:
        return None

    interval = [0, 0, 0, 0]  # years, months, weeks, days
    line = s.strip().split(" ")
    number = int(line[num_pos])
    text = line[text_pos][0]
    if text in "Dd":
        interval[3] = number
    elif text in "Ww":
        interval[2] = number
    elif text in "Mm":
        if len(line) > 2:
            # last day of month
            interval[1] = number
            interval[3] = -1
        else:
            interval[1] = number
    elif text in "Yy":
        interval[0] = number
    elif text in "Ll":
        interval[1] = number
        interval[3] = -1
    return relativedelta(
        years=interval[0], months=interval[1], weeks=interval[2], days=interval[3]
    )


def write(task, filename, verbose):
    toml.dump(task, open(filename, "w"))


def from_file(filename):
    task = default.copy()
    task.update(toml.load(filename))
    return task


def delete(task, filename, verbose):
    os.remove(filename)
    if verbose:
        print("  -> file {} deleted".format(filename.split("/")[-1]))


def execute_task(task, api, verbose, filename, forward=0):
    due_date = parse(task["due_date"]).date()
    early = string_to_relativedelta(task["early"])
    todoist_project = None
    new_task = task.copy()
    rewrite = False
    interval = string_to_relativedelta(task["interval"])
    while date.today() + relativedelta(days=forward) >= due_date - early:
        if todoist_project is None:
            todoist_project = api.projects.get(task["project"])
        if task["interval"] is None:
            # One time task
            for t in task["tasks"]:
                api.create_task(t, todoist_project, task["due_date"], task["priority"])
                if verbose:
                    print("  -> added task with due date {}".format(task["due_date"]))
            delete(task, filename, verbose)
            break

        else:
            # Recurring task
            tasks = new_task["tasks"][new_task["index"]]
            if isinstance(tasks, str):
                tasks = [tasks]
            for t in tasks:
                api.create_task(t, todoist_project, new_task["due_date"], new_task["priority"])
                if verbose:
                    print(
                        '  -> added task "{}" with due date {}'.format(
                            t, new_task["due_date"]
                        )
                    )
            # incrementing values
            if interval.days == -1:  # last day of month
                due_date += relativedelta(days=+1)
            due_date += interval
            new_task["due_date"] = due_date.isoformat()
            new_task["index"] = (new_task["index"] + 1) % len(new_task["tasks"])
            rewrite = True
    if rewrite:
        write(new_task, filename, verbose)

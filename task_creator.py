#!/usr/bin/env python3
from api import API
from datetime import date
from task import Task
import toml
import pathlib
import pickle
from enum import Enum


class TaskType(Enum):
    ONETIME = "o"
    RECURRING = "r"

    def __str__(self):
        return "one time" if self.name == "ONETIME" else "recurring"


def create_task():
    directory = pathlib.Path(__file__).resolve().parent
    conf = toml.load(str(directory / "todoist_scheduler.conf"))
    print("Logging to Todoist.")
    api = API(pickle.load(open(conf["token"], "rb")))
    if api.valid:
        projects = list(api.projects.keys())
        add_new_task = True
        while add_new_task:
            # Tasks
            print("Enter one task per line. Add empty line to finish.")
            tasks = []
            task = input("Task: ")
            while task != "":
                tasks.append(task)
                task = input("Task: ")
            # Project
            print("Your Todoist projects:")
            for i, proj in enumerate(projects):
                print("{} - {}".format(i, proj))
            project_number = input(
                "To which project would you like to add a task? (enter a number): "
            )
            while project_number == "" or int(project_number) not in range(
                len(projects)
            ):
                project_number = input("Project does not exist. Try again. ")
            project_number = int(project_number)
            # Due date
            due_date = input("What is a due date? In YYYY-MM-DD format: ").strip()
            # Task type
            task_type = input("[O]ne-time or [R]ecurring task? (default is one-time): ")
            task_type = "o" if task_type == "" else task_type[0].lower()
            while task_type not in "or":
                task_type = input(
                    "Wrong input. Input 'o' for one time task or 'r' for recurring task: "
                )
            task_type = TaskType(task_type)
            # Repeat interval
            if task_type == TaskType.RECURRING:
                interval = input(
                    "What should be the repetition interval? (input can be such as '1 day', '2W' or '1 month on the last day'): "
                )
            # Early
            early = input(
                "How early should be task added to Todoist? (defaults to 1 day): "
            )
            early = "1 day" if early == "" else early
            # Priority
            priorities = {
                0: "no priority",
                1: "low priority",
                2: "normal priority",
                3: "high priority",
                4: "very high priority",
            }
            print("What should be the task priority?")
            for key, value in priorities.items():
                print("{} - {}".format(key, value))
            priority = input("(defaults to normal priority): ")
            priority = (
                2 if priority == "" or int(priority) not in range(5) else int(priority)
            )
            task_plural = "tasks" if len(tasks) > 1 else "task"
            tasks_string = ", ".join(tasks)
            print(
                "Do you want to add {} task to project {} with due date {} posting it {} early containing {}: {} with {}".format(
                    task_type,
                    projects[project_number],
                    due_date,
                    early,
                    task_plural,
                    tasks_string,
                    priorities[priority],
                ),
                end="",
            )
            if task_type == TaskType.RECURRING:
                print(" and with interval of repetition {}".format(interval), end="")
            confirmation = input("? (Y/n) ")
            if confirmation == "" or confirmation[0] in "Yy":
                filename = pathlib.Path(conf["tasks_directory"]) / "{}_{}.toml".format(date.today().isoformat(), tasks[0])
                task = {
                    "project": projects[project_number],
                    "tasks": tasks,
                    "due_date": due_date,
                    "early": early,
                    "priority": priority,
                }
                if task_type == TaskType.RECURRING:
                    task["interval"] = interval
                    task["index"] = 0
                todoist_task = Task(api, filename, False, **task)
                todoist_task.write()
                todoist_task.execute()
                new_task = input("Would you like to add another task? (y/N) ")
                if new_task == "":
                    add_new_task = False
                elif new_task[0] in "Yy":
                    add_new_task = True
                else:
                    add_new_task = False
                # os.system("cls" if os.name == "nt" else "clear")
            else:
                add_new_task = True


if __name__ == "__main__":
    create_task()

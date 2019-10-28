import toml
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from datetime import datetime

default_template = {"name": "Template", "priority": 2, "tasks": []}


def taskdelta(task):
    when = task["when"] if "when" in task else 0
    return relativedelta(days=when)


def execute_template(filename, api):
    template = default_template.copy()
    template.update(toml.load(filename))
    if "due_date" in template:
        due_date = parse(template["due_date"]).date()
    else:
        due_date = datetime.now().date()
    project_name = "{} {}".format(template["name"], due_date)
    try:
        print("Creating project {}".format(project_name))
        project_id = api.create_project(project_name)
        for task in template["tasks"]:
            if "task" in task:
                priority = task["priority"] if "priority" in task else template["priority"]
                task_date = due_date + taskdelta(task)
                if isinstance(task["task"], str):
                    task["task"] = [task["task"]]
                for name in task["task"]:
                    api.create_task(name, project_id, task_date, priority)
                    print('-> Added new task "{}" with due date {}.'.format(name, task_date))
    except Exception as e:
        print(e)
        exit(1)

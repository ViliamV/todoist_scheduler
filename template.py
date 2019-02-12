from pytodoist import todoist
import toml
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from datetime import datetime

default_template = {
    "name": "Template",
    "priority": todoist.Priority.NORMAL,
    "color": "LIGHT_BLUE",
    "tasks": [],
}


def taskdelta(task):
    when = task["when"] if "when" in task else 0
    return relativedelta(days=when)


def execute_template(filename, user):
    template = default_template.copy()
    template.update(toml.load(filename))
    if "due_date" in template:
        due_date = parse(template["due_date"]).date()
    else:
        due_date = datetime.now().date()
    project_name = "{} {}".format(template["name"], due_date)
    try:
        print("Creating project {}".format(project_name))
        todoist_color = (
            template["color"]
            if hasattr(todoist.Color, template["color"])
            else "LIGHT_BLUE"
        )
        project = user.add_project(
            project_name, color=getattr(todoist.Color, todoist_color)
        )
        for task in template["tasks"]:
            if "task" in task:
                priority = (
                    task["priority"] if "priority" in task else template["priority"]
                )
                task_date = due_date + taskdelta(task)
                if isinstance(task["task"], str):
                    task["task"] = [task["task"]]
                for name in task["task"]:
                    project.add_task(name, date=task_date, priority=priority)
                    print(
                        '-> Added new task "{}" with due date {}.'.format(
                            name, task_date
                        )
                    )
    except Exception as e:
        print(e)
        exit(1)

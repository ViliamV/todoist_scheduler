from pytodoist import todoist
import toml
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from datetime import datetime

default_template = {
    "name": None,
    "priority": todoist.Priority.NORMAL,
    "color": 'LIGHT_BLUE',
    "tasks": []
}

def taskdelta(task):
    when = task['when'] if 'when' in task else 0
    return relativedelta(days=when)

def execute_template(filename, user, due_date):
    template = default_template.copy()
    template.update(toml.load(filename))
    if due_date is not None:
        due_date = parse(due_date).date()
    else:
        print('No date for the project, starting today.')
        due_date = datetime.now().date()
    project_name = f'{template["name"]} {due_date}'
    try:
        print(f'Creating project {project_name}')
        project = user.add_project(project_name, color=getattr(todoist.Color, template['color']))
        for task in template['tasks']:
            priority = task['priority'] if 'priority' in task else template['priority']
            task_date = due_date + taskdelta(task)
            name = task['task'] if 'task' in task else 'Empty task'
            project.add_task(name, date=task_date, priority=priority)
            print(f'-> Added new task "{name}" with due date {task_date}.')
    except Exception as e:
        print(e)
        exit(1)

#!/usr/bin/env python3
import os
from datetime import date
from pytodoist import todoist
from task import *
import toml
import os
import pickle

directory = os.path.dirname(os.path.realpath(__file__))
with open(directory + '/todoist_scheduler.conf') as f:
    conf = toml.loads(f.read())
print('Logging to Todoist.')
token = pickle.load(open(conf['login'], 'rb'))
user = todoist.login_with_api_token(token)
projects = [p.name for p in user.get_projects()]
add_new_task = True
while add_new_task:
    task_type = input('Input \'O\' for one time task or \'R\' for recurring task: ')
    while task_type not in 'oOrR':
        task_type = input('Wrong input. Input \'O\' for one time task or \'R\' for recurring task: ')
    print('These are your Todoist projects:')
    #print(list(zip(range(1, len(projects) + 1), projects)))
    for i, proj in enumerate(projects):
        print('{} - {}'.format(i, proj))
    project_number = int(input('To which project would you like to add a task? (enter a number): '))
    while project_number not in range(len(projects)):
        project_number = int(input('Project does not exist. Try again. '))
    due_date = input('What is a due date? In YYYY-MM-DD format: ').strip()
    early = input('How early should be task added to Todoist? (input can be such as \'3 days\' or \'1 W\'): ')
    print('Now you can add as many tasks as you want. When finished, input empty line.')
    tasks = []
    task = input('Task: ')
    while task != '':
        tasks.append(task)
        task = input('Task: ')
    if task_type in 'rR':
        interval = input('What should be the repetition interval? (input can be such as \'1 day\', \'2 W\' or \'1 month on the last day\'): ')
    priorities = {0: 'no priority', 1: 'low priority', 2: 'normal priority', 3: 'high priority', 4: 'very high priority'}
    print('What should be the task priority?')
    for key, value in priorities.items():
        print('{}={}'.format(key, value))
    priority = input('or leave empty for default (normal priority): ')
    if priority == '' or int(priority) not in range(5):
        priority = 2
    else:
        priority = int(priority)
    task_type_name = 'one time' if task_type in 'oO' else 'recurring'
    task_plural = 'tasks' if len(tasks)>1 else 'task'
    tasks_string = ', '.join(tasks)
    print('Do you want to add {} task to project {} with due date {} posting it {} early containing {}: {} with {}'.format(
        task_type_name, projects[project_number], due_date, early, task_plural, tasks_string, priorities[priority]), end = '')
    if task_type in 'rR':
        print(' and with interval of repetition {}'.format(interval), end='')
    confirmation = input('? (Y/n) ')
    if confirmation=='' or confirmation[0] in 'Yy':
        filename = '{}/{}_{}.toml'.format(conf['tasks_directory'],date.today().isoformat(), tasks[0])
        task = default.copy()
        task['project'] = name=projects[project_number]
        task['tasks'] = tasks
        task['due_date'] = due_date
        task['early'] = early
        if task_type in 'rR':
            task['interval'] = interval
            task['index'] = 0
        write(task, filename, False)
        execute(task, user, False, filename)
        new_task = input('Would you like to add another task? (y/N) ')
        if new_task == '':
            add_new_task = False
        elif new_task[0] in 'Yy':
            add_new_task = True
        else:
            add_new_task = False
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        add_new_task = True

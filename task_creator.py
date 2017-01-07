#!/usr/bin/env python3
import os
from datetime import date
from pytodoist import todoist
from task_class import *
import os
import pickle

directory = os.path.dirname(os.path.realpath(__file__))
with open(directory + '/todoist_scheduler.conf') as conf:
    for line in conf:
        if line[0] == 'O':
            one_time_dir = line[2:].strip()
        elif line[0] == 'R':
            recurring_dir = line[2:].strip()
print('Logging to Todoist.')
login, password = pickle.load(open(directory+'/login', 'rb'))
user = todoist.login(login, password)
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
    d = input('What is a due date? In YYYY-MM-DD format: ').split('-')
    due_date = date(int(d[0]), int(d[1]), int(d[2]))
    early = input('How early should be task added to Todoist? (input can be such as \'3 days\' or \'1 W\'): ')
    print('Now you can add as many tasks as you want. When finished, input empty line.')
    tasks = []
    task = input('Task: ')
    while task != '':
        tasks.append(task)
        task = input('Task: ')
    if task_type in 'oO':
        pass
    else:
        interval = input('What should be the repetition interval? (input can be such as \'1 day\', \'2 W\' or \'1 month on the last day\'): ')
    # Repeating
    task_type_name = 'one time' if task_type in 'oO' else 'recurring'
    task_plural = 'tasks' if len(tasks)>1 else 'task'
    tasks_string = ', '.join(tasks)
    print('Do you want to add {} task to project {} with due date {} posting it {} early containing {}: {}'.format(
        task_type_name, projects[project_number], due_date.isoformat(), early, task_plural, tasks_string), end = '')
    if task_type in 'rR':
        print(' with interval of repetition {}'.format(interval), end='')
    confirmation = input('? (Y/n) ')
    if confirmation=='' in 'Yy' or confirmation[0]:
        filename = '{}_{}.txt'.format(date.today().isoformat(), tasks[0])
        if task_type in 'oO':
            nt = OneTime(one_time_dir + '/' + filename, name=projects[project_number], tasks=tasks,
                         due_date=due_date, early=early)
            if not nt.execute(user, False, frontload=0):
                nt.write_task(False)
        else:
            nt = Recurring(recurring_dir + '/' + filename, name=projects[project_number], interval=interval,
                           tasks=tasks, due_date=due_date, early=early)
            nt.execute(user, False, frontload=0)
            nt.write_task(False)
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

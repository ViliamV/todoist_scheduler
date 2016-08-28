from pytodoist import todoist
import os
from datetime import date
from dateutil.relativedelta import relativedelta


class Recurring:
    def __init__(self, path, name=None, interval=None, tasks=None, due_date=None, early=None):
        self.path = path
        self.project_name = name if name is not None else ''
        if interval is None:
            self.interval = relativedelta(days=+7)
            self.interval_type = 0 #0-days, 1-weeks, 2-months, 3-years
        else:
            line_parse = interval.strip().split(' ')
            if len(line_parse) == 1:
                self.interval = relativedelta(days=+int(line_parse[0]))
                self.interval_type = 0
            elif len(line_parse) > 1:
                if line_parse[1][0] in 'Dd':
                    self.interval = relativedelta(days=+int(line_parse[0]))
                    self.interval_type = 0
                elif line_parse[1][0] in 'Ww':
                    self.interval = relativedelta(weeks=+int(line_parse[0]))
                    self.interval_type = 1
                elif line_parse[1][0] in 'Mm':
                    self.interval = relativedelta(months=+int(line_parse[0]))
                    self.interval_type = 2
                elif line_parse[1][0] in 'Yy':
                    self.interval = relativedelta(years=+int(line_parse[0]))
                    self.interval_type = 3        
        self.current = 0
        self.tasks = tasks if tasks is not None else []
        self.due_date = due_date if due_date is not None else date.today()
        if early is None:
            self.early = relativedelta(days=+1)
            self.early_type = 0 #0-days, 1-weeks, 2-months, 3-years
        else:
            line_parse = early.strip().split(' ')
            if len(line_parse) == 1:
                self.early = relativedelta(days=+int(line_parse[0]))
                self.early_type = 0
            elif len(line_parse) > 1:
                if line_parse[1][0] in 'Dd':
                    self.early = relativedelta(days=+int(line_parse[0]))
                    self.early_type = 0
                elif line_parse[1][0] in 'Ww':
                    self.early = relativedelta(weeks=+int(line_parse[0]))
                    self.early_type = 1
                elif line_parse[1][0] in 'Mm':
                    self.early = relativedelta(months=+int(line_parse[0]))
                    self.early_type = 2
                elif line_parse[1][0] in 'Yy':
                    self.early = relativedelta(years=+int(line_parse[0]))
                    self.early_type = 3  
        if name is None and interval is None and tasks is None and due_date is None and early is None:
            with open(path) as f:
                for line in f:
                    if line[0] == 'P':
                        self.project_name = line.strip()[2:]
                    elif line[0] == 'I':
                        line_parse = line.strip().split(' ')
                        if len(line_parse) == 2:
                            self.interval = relativedelta(days=+int(line_parse[1]))
                            self.interval_type = 0
                        elif len(line_parse) > 2:
                            if line_parse[2][0] in 'Dd':
                                self.interval = relativedelta(days=+int(line_parse[1]))
                                self.interval_type = 0
                            elif line_parse[2][0] in 'Ww':
                                self.interval = relativedelta(weeks=+int(line_parse[1]))
                                self.interval_type = 1
                            elif line_parse[2][0] in 'Mm':
                                self.interval = relativedelta(months=+int(line_parse[1]))
                                self.interval_type = 2
                            elif line_parse[2][0] in 'Yy':
                                self.interval = relativedelta(years=+int(line_parse[1]))
                                self.interval_type = 3
                    elif line[0] == 'T':
                        self.tasks.append(line.strip()[2:])
                    elif line[0] == 'C':
                        self.current = int(line.strip().split(' ')[1])
                    elif line[0] == 'D':
                        d = line.strip()[2:].split('-')
                        self.due_date = date(int(d[0]), int(d[1]), int(d[2]))
                    elif line[0] == 'E':                        
                        line_parse = line.strip().split(' ')
                        if len(line_parse) == 2:
                            self.early = relativedelta(days=+int(line_parse[1]))
                            self.early_type = 0
                        elif len(line_parse) > 2:
                            if line_parse[2][0] in 'Dd':
                                self.early = relativedelta(days=+int(line_parse[1]))
                                self.early_type = 0
                            elif line_parse[2][0] in 'Ww':
                                self.early = relativedelta(weeks=+int(line_parse[1]))
                                self.early_type = 1
                            elif line_parse[2][0] in 'Mm':
                                self.early = relativedelta(months=+int(line_parse[1]))
                                self.early_type = 2
                            elif line_parse[2][0] in 'Yy':
                                self.early = relativedelta(years=+int(line_parse[1]))
                                self.early_type = 3

    def write_task(self, verbose):
        if verbose: print('Writing the changes.')
        with open(self.path, 'w') as f:
            f.write('P {}\n'.format(self.project_name))
            if self.interval_type == 0:
                f.write('I {} D\n'.format(self.interval.days))
            elif self.interval_type == 1:
                f.write('I {} W\n'.format(self.interval.days//7))
            elif self.interval_type == 2:
                f.write('I {} M\n'.format(self.interval.months))
            elif self.interval_type == 3:
                f.write('I {} Y\n'.format(self.interval.years))            
            for task in self.tasks:
                f.write('T {}\n'.format(task))
            f.write('C {}\n'.format(self.current))
            f.write('D {}\n'.format(self.due_date.isoformat()))
            if self.early_type == 0:
                f.write('E {} D\n'.format(self.early.days))
            elif self.early_type == 1:
                f.write('E {} W\n'.format(self.early.days//7))
            elif self.early_type == 2:
                f.write('E {} M\n'.format(self.early.months))
            elif self.early_type == 3:
                f.write('E {} Y\n'.format(self.early.years)) 
        if verbose: print('Exiting.')

    def execute(self, user, verbose, frontload=0):
        r = False
        if frontload != 0 and verbose:
            print('Frontloading')
        for f in range(frontload + 1):
            if date.today() + relativedelta(days=f) >= self.due_date - self.early:
                if verbose: print('Action on date {}:'.format((date.today() + relativedelta(days=f)).isoformat()))
                todoist_project = user.get_project(self.project_name)
                new_task = self.tasks[self.current]
                due_date = self.due_date.isoformat()
                # maby due_date = max(self.due_date, date.today()).isoformat()
                todoist_project.add_task(new_task, date=due_date)
                if verbose: print('Added new task \'{}\' with due date {}.'.format(new_task, due_date))
                # incrementing values
                self.due_date = self.due_date + self.interval
                self.current = (self.current + 1) % len(self.tasks)
                r = True
            else:
                if verbose: print('No action needed on date {}.'.format((date.today() + relativedelta(days=f)).isoformat()))
        return r


class OneTime:
    def __init__(self, path, name=None, tasks=None, due_date=None, early=None):
        self.path = path
        self.project_name = name if name is not None else ''
        self.tasks = tasks if tasks is not None else []
        self.due_date = due_date if due_date is not None else date.today()
        if early is None:
            self.early = relativedelta(days=+1)
            self.early_type = 0 #0-days, 1-weeks, 2-months, 3-years
        else:
            line_parse = early.strip().split(' ')
            if len(line_parse) == 1:
                self.early = relativedelta(days=+int(line_parse[0]))
                self.early_type = 0
            elif len(line_parse) > 1:
                if line_parse[1][0] in 'Dd':
                    self.early = relativedelta(days=+int(line_parse[0]))
                    self.early_type = 0
                elif line_parse[1][0] in 'Ww':
                    self.early = relativedelta(weeks=+int(line_parse[0]))
                    self.early_type = 1
                elif line_parse[1][0] in 'Mm':
                    self.early = relativedelta(months=+int(line_parse[0]))
                    self.early_type = 2
                elif line_parse[1][0] in 'Yy':
                    self.early = relativedelta(years=+int(line_parse[0]))
                    self.early_type = 3  
        if name is None and tasks is None and due_date is None and early is None:
            with open(path) as f:
                for line in f:
                    if line[0] == 'P':
                        self.project_name = line.strip()[2:]
                    elif line[0] == 'T':
                        self.tasks.append(line.strip()[2:])
                    elif line[0] == 'D':
                        d = line.strip()[2:].split('-')
                        self.due_date = date(int(d[0]), int(d[1]), int(d[2]))                    
                    elif line[0] == 'E':                        
                        line_parse = line.strip().split(' ')
                        if len(line_parse) == 2:
                            self.early = relativedelta(days=+int(line_parse[1]))
                            self.early_type = 0
                        elif len(line_parse) > 2:
                            if line_parse[2][0] in 'Dd':
                                self.early = relativedelta(days=+int(line_parse[1]))
                                self.early_type = 0
                            elif line_parse[2][0] in 'Ww':
                                self.early = relativedelta(weeks=+int(line_parse[1]))
                                self.early_type = 1
                            elif line_parse[2][0] in 'Mm':
                                self.early = relativedelta(months=+int(line_parse[1]))
                                self.early_type = 2
                            elif line_parse[2][0] in 'Yy':
                                self.early = relativedelta(years=+int(line_parse[1]))
                                self.early_type = 3

    def write_task(self, verbose):
        if verbose: print('Writing the changes.')
        with open(self.path, 'w') as f:
            f.write('P {}\n'.format(self.project_name))
            for task in self.tasks:
                f.write('T {}\n'.format(task))
            f.write('D {}\n'.format(self.due_date.isoformat()))
            if self.early_type == 0:
                f.write('E {} D\n'.format(self.early.days))
            elif self.early_type == 1:
                f.write('E {} W\n'.format(self.early.days//7))
            elif self.early_type == 2:
                f.write('E {} M\n'.format(self.early.months))
            elif self.early_type == 3:
                f.write('E {} Y\n'.format(self.early.years)) 
        if verbose: print('Exiting.')

    def delete_file(self, verbose):
        if verbose: print('Removing file.')
        os.remove(self.path)
        if verbose: print('Exiting.')

    def execute(self, user, verbose, frontload=0):
        if frontload != 0 and verbose:
            print('Frontloading')
        if date.today() + relativedelta(days=frontload) >= self.due_date - self.early:
            if verbose: print('Action on date {}:'.format((date.today() + relativedelta(days=frontload)).isoformat()))
            todoist_project = user.get_project(self.project_name)
            due_date = self.due_date.isoformat()
            for task in self.tasks:
                todoist_project.add_task(task, date=due_date)
                if verbose: print('Added new task \'{}\' with due date {}.'.format(task, due_date))
            # incrementing values
            return True
        else:
            if verbose: print('No action needed on date {}.'.format((date.today() + relativedelta(days=frontload)).isoformat()))
            return False

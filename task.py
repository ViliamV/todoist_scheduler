#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import deltaparser
import pathlib
import toml


class Task:
    task_attrs = ["project", "tasks", "due_date", "early", "interval", "repeat", "index", "priority"]

    def __init__(self, api, filename, verbose, **kwargs):
        self._api = api
        self._file = pathlib.Path(filename)
        self._verbose = verbose
        # Task
        self.priority = 2
        self.project = None
        self.tasks = []
        self.due_date = None
        self.early = None
        self.interval = None
        self.repeat = None
        self.index = None
        for k, v in kwargs.items():
            if k in self.task_attrs:
                setattr(self, k, v)
        self._one_time_task = self.interval is None

    def write(self):
        data = {x: getattr(self, x) for x in self.task_attrs}
        toml.dump(data, self._file.open(mode="w"))

    def _delete(self):
        self._file.unlink()
        if self._verbose:
            print("  -> file {} deleted".format(self._file.name))

    def execute(self, forward=0):
        if self._one_time_task:
            self._execute_one_time(forward=forward)
        else:
            self._execute_recurring(forward=forward)

    def _execute_one_time(self, forward):
        todoist_project = self._api.projects.get(self.project)
        success = True
        for t in self.tasks:
            task_success = self._api.create_task(t, todoist_project, self.due_date, self.priority)
            if not task_success:
                success = False
            else:
                if self._verbose:
                    print("  -> added task with due date {}".format(self.due_date))
        if success:
            self._delete()

    def _execute_recurring(self, forward):
        due_date = parse(self.due_date).date()
        early = deltaparser.parse(self.early)
        rewrite = False
        interval = deltaparser.parse(self.interval)
        todoist_project = self._api.projects.get(self.project)
        goal_date = date.today() + relativedelta(days=forward)
        while goal_date >= due_date - early:
            tasks = self.tasks[self.index]
            if isinstance(tasks, str):
                tasks = [tasks]
            success = True
            for t in tasks:
                task_success = self._api.create_task(t, todoist_project, self.due_date, self.priority)
                if not task_success:
                    success = False
                else:
                    if self._verbose:
                        print(
                            '  -> added task "{}" with due date {}'.format(
                                t, self.due_date
                            )
                        )
            if success:
                # incrementing values
                if interval.days == -1:  # last day of month
                    due_date += relativedelta(days=+1)
                due_date += interval
                self.due_date = due_date.isoformat()
                self.index += 1
                self.index %= len(self.tasks)
                rewrite = True
        if rewrite:
            self.write()

    @classmethod
    def from_file(cls, filename, api, verbose):
        loaded = toml.load(str(filename))
        return cls(api, filename, verbose, **loaded)

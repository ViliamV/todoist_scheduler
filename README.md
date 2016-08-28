# Todoist Scheduler
Todoist Scheduler is a simple script that handles one-time and recurring tasks in plaintext and creates tasks in [Todoist](http://www.todoist.com) when they are needed.

## Dependencies
- [Dateutil](https://dateutil.readthedocs.io/en/stable/)
- [PyTodoist](https://github.com/Garee/pytodoist)

## Setup
1. Install the dependencies:
```bash
    $ pip install pytodoist python-dateutil
```
2. Download *.py files:
```bash
    $ git clone https://github.com/ViliamV/todoist_scheduler.git
    $ cd todoist_scheduler
```
3. Run todoist_scheduler.py with parameter '--first' and follow the instructions:
```bash
    $ ./todoist_scheduler.py --first
```
## Usage
You can create tasks using task_creator.py. They will be stored in directories found in todoist_scheduler.conf.
Each task is a separate plaintext file that can be easily modified.
To modify or create new task use these conventions:
- start each line with one of the symbols followed by space:
    - P - name of Todoist project. If in doubt, use Inbox.
    - I - for recurring tasks is interval of repetition. Followed by number and word (or starting letter of a word) day/week/month/year.
    - T - task/tasks. Add as many as you want.
    - C - if there are more tasks, this is an index of the next task to be processed. Use 0 if you creating a new task or ommit it.
    - D - ISO format of date of the due date of the next task
    - E - how many days in advance should be task put into Todoist. Followed by number and word (or starting letter of a word) day/week/month/year.

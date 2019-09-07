import uuid
import requests
import json


class API:
    def __init__(self, token):
        self.token = token
        self.projects = {}
        self.valid = self.verify_token()

    def _headers(self, post=True):
        headers = {
            "Authorization": "Bearer {}".format(self.token)
        }
        if post:
            headers.update({
                "Content-Type": "application/json",
                "X-Request-Id": str(uuid.uuid4()),
            })
        return headers

    def create_task(self, content, project, due_date, priority=2):
        response = requests.post(
        "https://api.todoist.com/rest/v1/tasks",
        data=json.dumps({
            "content": content,
            "project_id": project,
            "due_date": due_date,
            "priority": priority
        }),
        headers=self._headers())
        return response.status_code == 200

    def create_project(self, name, parent=None):
        if name not in self.projects.keys():
            data = {"name": name}
            if parent:
                data["parent"] = parent
            response = requests.post("https://api.todoist.com/rest/v1/projects",
                                     data=json.dumps(data), headers=self._headers())
            if response.status_code == 200:
                project_id = response.json().get("id")
                self.projects[name] = project_id
                return project_id

    def _get_projects(self):
        return requests.get("https://api.todoist.com/rest/v1/projects",
                            headers=self._headers(post=False))

    def get_projects(self):
        data = [(x["name"], x["id"]) for x in self._get_projects().json()]
        self.projects = {name: id for (name, id) in data}

    def verify_token(self):
        return self._get_projects().status_code == 200

    @classmethod
    def create_new(cls, directory, missing_conf=False, missing_location=False, missing_token=False):
        import pickle
        import os
        import toml

        dir = directory + "/tasks"
        if missing_conf:
            print("This is a Todoist Scheduler.")
            print("Creating default configuration file todoist_scheduler.conf")
            conf = {"tasks_directory": dir}
            toml.dump(conf, open("{}/todoist_scheduler.conf".format(directory), "w"))
            print("By default, tasks will be stored in directory:\n{}.".format(dir))
        if missing_location or missing_conf:
            conf = toml.load("{}/todoist_scheduler.conf".format(directory))
            conf["token"] = directory + "/token"
            toml.dump(conf, open("{}/todoist_scheduler.conf".format(directory), "w"))
        if missing_token or missing_location or missing_conf:
            print("Please enter your Todoist token.")
            print("It will be stored unencrypted as Python Pickle file so do not share the file 'token'")
            while True:
                token = input("Token: ")
                api = cls(token)
                if api.valid:
                    print("Login successful.")
                    pickle.dump(token, open(directory + "/token", "wb"))
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    return api
                else:
                    print("Login unsuccessful. Please, try again.")

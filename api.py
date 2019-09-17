import json
import requests
import uuid


class API:
    def __init__(self, token):
        self._token = token
        self.valid, self.projects = self._verify_and_load_projects()

    def _headers(self, post=True):
        headers = {"Authorization": "Bearer {}".format(self._token)}
        if post:
            headers.update(
                {
                    "Content-Type": "application/json",
                    "X-Request-Id": str(uuid.uuid4())
                }
            )
        return headers

    def _verify_and_load_projects(self):
        projects = {}
        response = requests.get(
            "https://api.todoist.com/rest/v1/projects",
            headers=self._headers(post=False),
        )
        valid = response.status_code == 200
        if valid:
            projects = {x["name"]: x["id"] for x in response.json()}
        return (valid, projects)

    def create_task(self, content, project, due_date, priority=2):
        response = requests.post(
            "https://api.todoist.com/rest/v1/tasks",
            data=json.dumps(
                {
                    "content": content,
                    "project_id": project,
                    "due_date": due_date,
                    "priority": priority,
                }
            ),
            headers=self._headers(),
        )
        return response.status_code == 200

    def create_project(self, name, parent=None):
        if name not in self.projects.keys():
            data = {"name": name}
            if parent:
                data["parent"] = parent
            response = requests.post(
                "https://api.todoist.com/rest/v1/projects",
                data=json.dumps(data),
                headers=self._headers(),
            )
            if response.status_code == 200:
                project_id = response.json().get("id")
                self.projects[name] = project_id
                return project_id

    @classmethod
    def create_new(
        cls,
        root,
        missing_conf=False,
        missing_location=False,
        missing_token=False
    ):
        import pickle
        import toml

        tasks_dir = root / "tasks"
        conf_file = root / "todoist_scheduler.conf"
        token_file = root / "token"
        if missing_conf:
            print("This is a Todoist Scheduler.")
            print("Creating default configuration file todoist_scheduler.conf")
            conf = {"tasks_directory": str(tasks_dir)}
            toml.dump(conf, conf_file.open(mode="w"))
            print("By default, tasks will be stored in directory:\n{}.".format(tasks_dir))
            tasks_dir.mkdir(parents=True, exist_ok=True)
        if missing_location or missing_conf:
            conf = toml.load(conf_file)
            conf["token"] = str(token_file)
            toml.dump(conf, conf_file.open(mode="w"))
        if missing_token or missing_location or missing_conf:
            print("Please enter your Todoist token.")
            print(
                "It will be stored unencrypted as Python Pickle file so do not share the file 'token'"
            )
            while True:
                token = input("Token: ")
                api = cls(token)
                if api.valid:
                    print("Login successful.")
                    pickle.dump(token, token_file.open(mode="wb"))
                    return api
                else:
                    print("Login unsuccessful. Please, try again.")

import requests

class AudioBookShelfService:
	def __init__(self, base_url):
		self.base_url = base_url

	def login(self, username, password):
		url = f"{self.base_url}/login"
		payload = {
			"username": username,
			"password": password
		}
		return self._post(url, payload).get("user")

	def logout(self, socketId=None):
		url = f"{self.base_url}/logout"
		payload = {}
		if socketId:
			payload["socketId"] = socketId
		self._post(url, payload)

	def initialize_server(self, new_root_username, new_root_password=""):
		url = f"{self.base_url}/init"
		payload = {
			"newRoot": {
				"username": new_root_username,
				"password": new_root_password
			}
		}
		self._post(url, payload)

	def server_status(self):
		url = f"{self.base_url}/status"
		return self._get(url)        

	def ping(self):
		url = f"{self.base_url}/ping"
		return self._get(url)

	def healthcheck(self):
		url = f"{self.base_url}/healthcheck"
		self._get(url)

	def _post(self, url, payload=None):
		headers = {"Content-Type": "application/json"}
		response = requests.post(url, headers=headers, json=payload)
		response.raise_for_status()
		return response.json()

	def _get(self, url):
		response = requests.get(url)
		response.raise_for_status()
		return response.json()

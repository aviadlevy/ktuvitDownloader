import requests

URL = "http://www.ktuvit.com/"
URL_LOGIN = "http://www.ktuvit.com/login.php"


class Connection(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.s = requests.Session()

    def login(self):
        self.s.post(URL_LOGIN, {"email": self.username, "password": self.password, "Login": "%D7%94%D7%AA%D7%97%D7%91%D7%A8"})
        print self.s.get(URL)

    def close(self):
        self.s.close()

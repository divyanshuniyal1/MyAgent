# auth/models.py

class SSOUser:
    def __init__(self, email: str, name: str):
        self.email = email
        self.name = name
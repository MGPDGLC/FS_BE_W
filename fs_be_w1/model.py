# coding: utf8
class User:
    def __init__(self, name=None, pwd=None, email=None,
                 age=None, birthday=None, face=None):
        self.name = name
        self.pwd = pwd
        self.email = email
        self.age = age
        self.birthday = birthday
        self.face = face

    def toList(self):
        return [self.name, self.pwd, self.email, self.age, self.birthday, self.face]

    def fromList(self, user_info):
        self.name = user_info[0]
        self.pwd = user_info[1]
        self.email = user_info[2]
        self.age = user_info[3]
        self.birthday = user_info[4]
        self.face = user_info[5]

    def getAttrs(self):
        return ('name', 'pwd', 'email', 'age', 'birthday', 'face')




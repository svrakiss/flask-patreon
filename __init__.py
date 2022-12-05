from flask import Flask
class MyApp(Flask):
    def __init__(self):
        Flask.__init__(self,__name__)

app = MyApp()
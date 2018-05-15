# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 19:23:04 2016
## please note that the localhost address is not 0.0.0.0 but http://127.0.0.1:[port number]/
@author: guoxuan
"""

import web

urls = (
    '/', 'index',
    '/add','add',)

class index:
    def GET(self):
       render = web.template.render('templates/')
       name = 'xiaofeima '    
       return render.index(name)
       # return "Hello, world!"
class add:
    def post(self):
        data=web.input()
        

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
import time
import json
from TemplateEngine.Render import *

class Html:
    def __init__(self,text) -> None:
        self.text = text
    
    def __str__(self) -> str:
        return self.text

class Json:
    def __init__(self,obj) -> None:
        self.obj = obj
    
    def __str__(self) -> str:
        return json.dumps(self.obj)

class Light:
    def __init__(self) -> None:
        self.routeList = dict()
        self.renderList = dict()
        self.commonLibrary = Library()
        self.status = 'HTTP/1.1 200 OK'
        self.contentType = 'text/html'

    def application(self,env,start_response):
        # print(env)
        request = env['request']
        method = request['method']
        url = request['url']
        body = request['body']
        print("method: " + method," url: " + url,"body: " + body)
        response_body = self.response(method,url,body)
        response_headers = [('Server', 'bfe/1.0.8.18'), ('Date', '%s' % time.ctime()), ('Content-Type', self.contentType)]
        start_response(self.status, response_headers)

        return response_body

    def registerFilter(self,target):
        def register(k,v):
            self.commonLibrary.registerFilter(k,v)
        if(callable(target)):
            return register(target.__name__, target)
        else:
            return lambda x : register(target, x)

    def registerTag(self,target):
        def register(k,v):
            self.commonLibrary.registerTag(k,v)
        if(callable(target)):
            return register(target.__name__, target)
        else:
            return lambda x : register(target, x)

    def render(self,temeplteName,context):
        body = ''
        if(temeplteName in self.renderList):
            body = self.renderList[temeplteName].render(context,self.commonLibrary)
        else:
            render = Render(temeplteName)
            render.compile()
            self.renderList[temeplteName] = render
            body = self.renderList[temeplteName].render(context,self.commonLibrary)
        return Html(body)

    def show_routeList_keys(self):
        print("show_routeList_keys::",self.requestList.keys())

    def request(self,target):
        def register(k,v):
            self.routeList[k] = v
        if(callable(target)):
            return register('/' + target.__name__, target)
        else:
            return lambda x : register(target, x)

    def response(self,method,path,body):
        # return self.routeList[path]() #TODO: *args 404 and others
        if(path in self.routeList):
            responseBody = self.routeList[path]()
            if(isinstance(responseBody,Html)):
                self.contentType = 'text/html'
            elif(isinstance(responseBody,Json)):
                self.contentType = 'text/json'
            return str(responseBody)
        else:
            return self.notFound()
    
    def notFound(self):
        self.status = 'HTTP/1.1 404 NotFound'
        return '<html><body><h1>404<h1></body></html>'
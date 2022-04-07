import time
from TemplateEngine.Render import *

class Light:
    def __init__(self) -> None:
        self.routeList = dict()
        self.renderList = dict()
        self.commonLibrary = Library()
        self.status = 'HTTP/1.1 200 OK'

    def application(self,env,start_response):
        # print(env)
        request = env['request']
        method = request['method']
        url = request['url']
        body = request['body']
        print(method,url,body)
        response_headers = [('Server', 'bfe/1.0.8.18'), ('Date', '%s' % time.ctime()), ('Content-Type', 'text/html')]
        start_response(self.status, response_headers)
        response_body = self.response(url)

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
        if(temeplteName in self.renderList):
            return self.renderList[temeplteName].render(context,self.commonLibrary)
        else:
            render = Render(temeplteName)
            render.compile()
            self.renderList[temeplteName] = render
            return self.renderList[temeplteName].render(context,self.commonLibrary)

    def show_routeList_keys(self):
        print("show_routeList_keys::",self.requestList.keys())

    def request(self,target):
        def register(k,v):
            self.routeList[k] = v
        if(callable(target)):
            return register('/' + target.__name__, target)
        else:
            return lambda x : register(target, x)

    def response(self,path,*args):
        # return self.routeList[path]() #TODO: *args 404 and others
        if(path in self.routeList):
            return self.routeList[path]()
        else:
            self.status = 'HTTP/1.1 404 NotFound'
            return '<html><body><h1>404<h1></body></html>'
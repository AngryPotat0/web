from TemplateEngine.Render import *

class Light:
    def __init__(self) -> None:
        self.routeList = dict()
        self.renderList = dict()
        self.commonLibrary = Library()

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
            return self.renderList[temeplteName](context,self.commonLibrary)
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
        return self.routeList[path]() #TODO: *args 404 and others
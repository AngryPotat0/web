import time
import datetime
from TemplateEngine.Render import *
from Light import *
from server import httpServer

light = Light()

def application():
    light.run()

@light.registerTag
def currentTime(*args):
    now_time = str(datetime.datetime.now())
    return now_time

@light.registerFilter("cashFormat")
def func(x):
    return "$" + str(x)

@light.request('/hello')
def fun():
    productList = [{"name":"book","price":12},{"name":"cup","price":22},{"name":"keyboard","price":530}]
    context = {"userName":"angryPotato","age":15,"productList":productList}
    return light.render('template.html',context)

@light.request('/jsonTest')
def js():
    return Json({ 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 })

application()
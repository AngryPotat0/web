import time
import datetime
from TemplateEngine.Render import *
from Light import *
from server import httpServer

light = Light()

@light.registerTag
def currentTime(*args):
    now_time = str(datetime.datetime.now())
    return now_time

@light.registerFilter("toM")
def func(x):
    return "$" + str(x)

@light.request('/hello')
def fun():
    productList = [{"name":"book","price":12},{"name":"cup","price":22},{"name":"keyboard","price":530}]
    context = {"userName":"angryPotato","age":15,"productList":productList}
    return light.render('template.html',context)

server =httpServer('localhost',8080,light.application)
server.run()

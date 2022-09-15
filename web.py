import datetime
from tkinter.messagebox import NO
from TemplateEngine.Render import *
from Light import *

light = Light()


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

@light.request('/show')
def fun():
    return light.render('show.html',None)

@light.request('/jsonTest')
def js():
    return Json({ 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 })

@light.request('/getJson')
def getJson(json_obj):
    return json.dumps(json_obj)

light.run()
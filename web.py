import datetime
from itertools import product
from multiprocessing import context
from tkinter.messagebox import NO
from TemplateEngine.Render import *
from Light import *
from database import *

light = Light()
db = Database("webDatabase.db")
conn = db.getDB()

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
    print(json.dumps(json_obj))
    return json.dumps(json_obj)

@light.request('/insert')
def insertProduct(json_obj):
    productList = json_obj['list']
    print(productList)
    for name in productList:
        conn.execute("insert into products(name) values (?)", (name,))
    conn.commit()

@light.request('/showProducts')
def showProducts():
    res = conn.execute('select * from products')
    res = list(res)
    productList = list()
    if(len(res) > 0):
        i = 1
        for row in res:
            productList.append({'id':i,"name":row[1]})
            i += 1
    context = {"productList":productList}
    return light.render('databaseTest.html',context)

light.run()
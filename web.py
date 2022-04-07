import time
import datetime
from TemplateEngine.Render import *
from Light import *

light = Light()

def application(env,start_response):
    # print(env)
    request = env['request']
    method = request['method']
    url = request['url']
    body = request['body']
    print(method,url,body)
    status = 'HTTP/1.1 200 OK'
    response_headers = [('Server', 'bfe/1.0.8.18'), ('Date', '%s' % time.ctime()), ('Content-Type', 'text/html')]
    start_response(status, response_headers)
    response_body = 'Default page'
    # response_body = 'Wait for it'
    if(url != '/default'): response_body = light.response(url)

    return response_body

@light.registerTag
def currentTime(*args):
    now_time = str(datetime.datetime.now())
    return now_time

# toM = lambda x: "$" + str(x)
# render.library.registerFilter("toM",toM)
@light.registerFilter("toM")
def func(x):
    return "$" + str(x)

@light.request('/hello')
def fun():
    # render.library.registerTag("currentTime",currentTime)
    productList = [{"name":"book","price":12},{"name":"cup","price":22},{"name":"keyboard","price":530}]
    context = {"userName":"angryPotato","age":15,"productList":productList}
    return light.render('template.html',context)

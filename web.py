import time
import datetime
from TemplateEngine.Render import *

def application(env,start_response):
    print(env)
    request = env['request']
    method = request['method']
    url = request['url']
    body = request['body']
    status = 'HTTP/1.1 200 OK'
    response_headers = [('Server', 'bfe/1.0.8.18'), ('Date', '%s' % time.ctime()), ('Content-Type', 'text/html')]
    start_response(status, response_headers)

    response_body = str(fun())
    return response_body

def fun():
    render = Render("template.html")
    render.compile()

    # render.library.registerTag("currentTime",currentTime)
    @render.registerTag
    def currentTime(*args):
        now_time = str(datetime.datetime.now())
        return now_time

    # toM = lambda x: "$" + str(x)
    # render.library.registerFilter("toM",toM)
    @render.registerFilter("toM")
    def func(x):
        return "$" + str(x)


    productList = [{"name":"book","price":12},{"name":"cup","price":22},{"name":"keyboard","price":530}]
    context = {"userName":"angryPotato","age":15,"productList":productList}

    html = render.render(context)
    return html

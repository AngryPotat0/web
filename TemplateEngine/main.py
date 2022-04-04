from Render import *
import datetime

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
print(html)

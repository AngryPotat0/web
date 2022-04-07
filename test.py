def fun(a,b,c):
    print("In func:",a,b,c)

def response(path,*args):
        print("path:",path)
        fun(args)

response('/hello','a',1,3.7)
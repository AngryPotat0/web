# python_source = """\
# SEVENTEEN = 17

# def three():
#     return 3
# """
# global_namespace = {}
# exec(python_source, global_namespace)
# print(global_namespace['SEVENTEEN'])
# print(global_namespace['three']())
# t = "12"
# print("""result.append(%s)""" % repr(t))
#lis = {"a":1,"b":2}
#print(getattr(lis, "keys"))

#a = "123.45"
#print(a.isdigit())
def tes(*tes):
    print(tes[0],tes[1])

tes('a','b')
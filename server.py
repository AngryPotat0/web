from cmath import e
import socket
import os
from os.path import dirname, abspath
script_path = abspath(dirname(__file__))

class httpServer:
    def __init__(self,ip: str, port: int,application=None):
        self.file_type = {
            'jpg': 'image/jpeg',
            'png': 'image/png',
            'html': 'text/html'
        }
        self.application = application
        self.response_status = ''
        self.response_header = ''
        self.web_root_path = ''
        self.setting()
        self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.soc.bind((ip,port))

    def setRootPath(self,path='static'):
        # self.web_root_path = os.path.join(script_path, path)
        self.web_root_path = script_path + "/" + path

    def setting(self):#TODO: 读取配置文件
        text = ""
        root_path = 'static'
        try:
            f = open("setting.ini",'r')
            text = f.read().split('\r\n')
        except Exception:
            print("Error in settings")
        for line in text:
            k,v = line.split('=')
            if(k == 'root'):
                root_path = v
        self.setRootPath(root_path)

    def run(self):
        print("Http Server start running")
        while(True):
            self.soc.listen(5)
            conn,addr = self.soc.accept()
            request = str(conn.recv(1024), encoding = "utf-8")
            # print(request)
            request = self.parseRequest(request,addr)
            if(not request):
                print("request error")
                conn.close()
            # url_type = request['url'].split('.')[-1]
            temp = request['url'].split('.')
            url_type = temp[-1] if len(temp) > 1 else 'py'
            if(url_type == 'py'):
                try:
                    # py_name = request['url'][1:-3] # FIXME:
                    # py_module = __import__(py_name)
                    env = {'request':request}
                    response_body = self.application(env,self.start_response)
                    response = bytes(self.response_status + os.linesep + self.response_header + os.linesep + response_body, encoding="utf-8")
                    conn.sendall(response)
                    conn.close()
                except ImportError:
                    print("Import error")
                    response = bytes("HTTP/1.1 404 Not Found" + os.linesep, encoding="utf-8")
                    conn.sendall(response)
                    conn.close()
            else:
                try:
                    file_type = ""
                    if(url_type in self.file_type):
                        file_type = self.file_type[url_type]
                    else:
                        file_type = 'text\html'

                    response = bytes('HTTP/1.1 200 OK' + os.linesep + 'Content-Type:%s'% file_type + os.linesep + os.linesep, encoding="utf-8")
                    file = request['url'] if request['url'] != '/' else '/index.html'

                    temp = self.loadFile(file)
                    if(temp != None):
                        if(isinstance(temp,str)):
                            response += bytes(temp,encoding="utf-8")
                        else:
                            response += temp
                    else:
                        response = bytes("HTTP/1.1 404 Not Found" + os.linesep, encoding="utf-8")
                    conn.sendall(response)
                    conn.close()
                except:
                    print("Unknow error")
                    response = bytes("HTTP/1.1 404 Not Found" + os.linesep, encoding="utf-8")
                    conn.sendall(response)
                    conn.close()

    def parseRequest(self,request,addr):
        # print(request)
        request_split = request.split('\r\n')
        method, url, version = request_split[0].split(' ')

        requestHead = dict()

        for i in range(1, len(request_split)):
            if (request_split[i] == ''):
                break
            key, value = request_split[i].split(': ')
            requestHead[key] = value

        requestBody = []
        for i in range(2 + len(requestHead), len(request_split)):
            requestBody.append(request_split[i])
        requestBody = '\r\n'.join(requestBody)

        ans = {
            'addr': addr,
            'method': method,
            'url': url,
            'http_version': version,
            'head': requestHead,
            'body': requestBody
        }
        return ans

    def loadFile(self,file_path):
        file_path = self.web_root_path + "/" + file_path
        img_file = ('jpg', 'png', 'ico')
        audio_file = ('wav')
        file_type = file_path.split('.')[-1]
        file = None
        try:
            if(file_type in img_file or file_type in audio_file):
                f = open(file_path, 'rb')
            else:
                f = open(file_path,'r')
            file = f.read()
            f.close()
        except Exception:
            pass
        return file

    def start_response(self, status, response_headers):
        self.response_status = status
        self.response_header = ''
        for k, v in response_headers:
            kv = k + ':' + v + os.linesep
            self.response_header += kv

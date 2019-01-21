#  coding: utf-8
import socketserver
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
class Response():

    def __init__(self, status, body):

        self.status = status
        self.header_dic = self.base_response_dic()
        self.body = body

    def base_response_dic(self):
        r_dic = {
        "Server":None,
        "Date":None,
        "Content-Type":None,
        "Content-Length":None,
        }

        return r_dic

    def header_to_string(self):

        header_string = self.status + "\r\n"

        for key, value in self.header_dic.items():
            if value is not None:
                header_string += "{0}: {1}\r\n".format(key, value)
        header_string += "\r\n"

        return header_string

    def response_string(self):
        return self.header_to_string() + self.body


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))

        with open('www/index.html', 'r') as file:
            #string = file.read()
            #arr = bytearray(file)
            #self.request.sendall(bytes(file))
            #self.request.sendall(bytes(200))
            # response = """HTTP/1.1 200 OK\r\n\
            # Date: {DATE}\r\n\
            # Content-Type: text/plain\r\n\
            # \r\n\
            # HELLO\r\n\
            # """.format(DATE=self.get_date())

            # response = self.response_header_200()
            # response = response + "SUP\r\n"
            # print(response)
            # self.request.sendall(bytearray(response, 'utf-8'))

            #body = "LETS GO OILERS"

            # body = file.read()
            # header_string = self.response_header_200(body)
            # #print(response)
            # header_string += body
            # self.request.sendall(bytearray(header_string, 'utf-8'))

            status = "HTTP/1.1 200 OK"
            body = file.read()

            """ response object """
            res_obj = Response(status, body)
            res_obj.header_dic["Server"] = "Nicks_Macbook_Pro"
            res_obj.header_dic["Date"] = str(self.get_date())
            res_obj.header_dic["Content-Type"] = "text/plain"
            res_obj.header_dic["Content-Length"] = str(len(body.encode('utf-8')))

            response_string = res_obj.response_string()
            print(response_string)
            self.request.sendall(bytearray(response_string, 'utf-8'))






    """
    https://stackoverflow.com/questions/225086/rfc-1123-date-representation-in-python
    """
    def get_date(self):
        now = datetime.now()
        stamp = mktime(now.timetuple())
        return format_date_time(stamp)

    # def base_response_dic(self):
    #     r_dic = {
    #     "Server":None,
    #     "Date":None,
    #     "Content-Type":None,
    #     "Content-Length":None,
    #     }
    #
    #     return r_dic
    #
    # """
    # returns a http string response
    # https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only
    # """
    # def response_header_200(self, body):
    #
    #
    #     r_dic = self.base_response_dic()
    #
    #     status = "HTTP/1.1 200 OK"
    #     r_dic["Server"] = "Nicks_Macbook_Pro"
    #     r_dic["Date"] = str(self.get_date())
    #     r_dic["Content-Type"] = "text/html"
    #     r_dic["Content-Length"] = str(len(body.encode('utf-8')))
    #
    #     response_string = self.header_to_string(status, r_dic)
    #
    #     return response_string
    #
    # def header_to_string(self, status, dic_obj):
    #
    #     header_string = status + "\r\n"
    #
    #     # PCT = dic_obj["Protocol"] + dic_obj["R_Code"] + dic_obj["R_Text"] + "\r\n"
    #     # response_string += PCT
    #
    #     for key, value in dic_obj.items():
    #         header_string += "{0}: {1}\r\n".format(key, value)
    #
    #     header_string += "\r\n"
    #     #response_string += "HELLO MY NAME IS NICK"
    #
    #
    #     return header_string




if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

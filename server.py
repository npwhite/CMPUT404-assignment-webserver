#  coding: utf-8
import socketserver
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import os



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


REDIRECTS = {
"":""
}
ROOT = "www"
HOST, PORT = "localhost", 8080


# try: curl -v -X GET http://127.0.0.1:8080/
class Response():

    def __init__(self, status, body):
        self.status = status
        self.body = body
        self.header_dic = {
        "Server":"Nicks_Macbook_Pro",
        "Date":self.get_date(),
        "Content-Type":None,
        "Content-Length":str(len(self.body.encode('utf-8'))),
        }

    """
    https://stackoverflow.com/questions/225086/rfc-1123-date-representation-in-python
    """
    def get_date(self):
        now = datetime.now()
        stamp = mktime(now.timetuple())
        return str(format_date_time(stamp))


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
        print("--------- RECIEVED ---------")
        print(self.data.decode('utf-8'))
        print()

        request_dic = {}
        request_list = self.data.decode('utf-8').split("\r\n")
        request_line = request_list[0]

        for i in range(1, len(request_list), 1):
            key, value = request_list[i].split(":", 1)
            request_dic[key] = value

        print(request_line)
        method, uri, http_version = request_line.split()

        requested_path = ROOT + uri
        print("requested_path = {}".format(requested_path))
        """ Authenticate path permission """
        file = self.check_file_access(requested_path)
        print("FILE DIC = {}".format(file))

        if file["EXISTS"] and file["AUTH"]:
            with open(requested_path, 'r') as file_obj:
                self.handle_200_response(file_obj)

        elif file["EXISTS"] and not file["AUTH"]:
            """ could do 403 forbidden but tests expect 404 """
            self.handle_404_response()

        elif not file["EXISTS"]:

            redirect = self.reroute(uri)                                       # WARNING: test this well
            routed_file_perm = self.check_file_access(ROOT + redirect)
            print("---------- REDIRECT = {} -----------".format(redirect))

            if routed_file_perm["EXISTS"] and routed_file_perm["AUTH"]:
                print("301 ISSUED----------------------")
                self.handle_301_response(redirect)

            elif routed_file_perm["EXISTS"] and not routed_file_perm["AUTH"]:
                self.handle_404_response()

            elif not routed_file_perm["EXISTS"]:
                self.handle_404_response()


    def handle_200_response(self, file):
        status = "HTTP/1.1 200 OK"
        body = file.read()
        type = file.name.split(".")[-1]

        """ response object """
        res_obj = Response(status, body)
        res_obj.header_dic["Content-Type"] = "text/{}".format(type)
        response_string = res_obj.response_string()

        self.request.sendall(bytearray(response_string, 'utf-8'))
        print()
        print("DATA SENT")


    def handle_301_response(self, file_route):
        status = "HTTP/1.1 301 Moved Permanently"

        res_obj = Response(status, "ITEM WAS MOVED PERMANENTLY\n")
        """ type should be 301 respones body type, not type of the file requested """
        res_obj.header_dic["Content-Type"] = "text/plain"
        res_obj.header_dic["Location"] = "http://{}:{}{}".format(HOST, str(PORT), file_route)
        response_string = res_obj.response_string()

        self.request.sendall(bytearray(response_string, 'utf-8'))
        print()
        print("DATA SENT")
        print(response_string)


    def handle_404_response(self):
        status = "HTTP/1.1 404 Not Found"

        res_obj = Response(status, "ERROR 404 NOT FOUND\n")
        res_obj.header_dic["Content-Type"] = "text/plain"
        response_string = res_obj.response_string()

        self.request.sendall(bytearray(response_string, 'utf-8'))
        print()
        print("DATA SENT")
        print(response_string)


    def check_file_access(self, requested_path):
        valid_file = {
        "EXISTS":os.path.isfile(requested_path),
        "AUTH":self.in_directory(requested_path, ROOT),
        }
        return valid_file


    # ----- CITATION:-----
    # LINK: https://stackoverflow.com/questions/3812849/how-to-check-whether-a-directory-is-a-sub-directory-of-another-directory
    # USERS: simon, blaze
    def in_directory(self, file, directory):
        """
        Given a file and directory path, determines if the file belongs to the directory
        Arguments:
            file : str
                - the file we are checking
            directory : str
                - the directory we are checking
        Return:
            bool - True if the file is contained in the directory
        """
        directory = os.path.join(os.path.realpath(directory), '')
        file = os.path.realpath(file)
        return os.path.commonprefix([file, directory]) == directory



    def reroute(self, uri):
        """
        Edits the passed uri to more-likely represent a findable file
        """

        if uri[-1] == '/':
            """ directory suspected, default index.html """
            uri += "index.html"
        elif len(uri.split('.')):
            """ directory suspected, default index.html """
            uri += "/index.html"

        return uri



if __name__ == "__main__":

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

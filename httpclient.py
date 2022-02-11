#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re

# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # connect to server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # get the code from response
        data_list = data.split("\r\n")
        data_list = data.split()
        code = int(data_list[1]) # get the code section
        return code

    def get_headers(self,data):
        # get headers from response
        return data.split("\r\n\r\n")    

    def get_port(self, url_req):
        # gets the port value from the url
        port = url_req.port
        if port == None:
            port = 80
        return port

    def get_body(self, data):
        return data[1]
        
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')


    def send_receive(self, hostname, port, payload):
        # connect to server, send payload, and receive the data
        self.connect(hostname, port)
        self.socket.sendall(payload.encode())
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall(self.socket)
        self.close()
        headers = self.get_headers(data)
        code = self.get_code(headers[0])
        body = self.get_body(headers)
        return code,body
    
    def get_path(self, url_req):
        path = url_req.path
        if path == '':
            path = '/'
        return path
    
    def get_query(self, url_req):
        query = url_req.query
        if query != '':
            query = "?"+query
        return query

    def GET(self, url, args=None):
        # makes GET request to specified location

        url_req = urllib.parse.urlparse(url)
        hostname = url_req.hostname
        port = self.get_port(url_req)
        path = self.get_path(url_req)
        query = self.get_query(url_req)

        if args != None:
            string = urllib.parse.urlencode(args)
            if query != '':
                # have query in url parameter and ask arguements passed in
                query += "&" + string
            else:
                # have query parameters as arguements passed in 
                query = "?" + string 

        payload = f"GET {path}{query} HTTP/1.1\r\nHost: {hostname}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n" 

        # send and receive the data from the host
        code,body = self.send_receive(hostname, port, payload)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        url_req = urllib.parse.urlparse(url)
        path = self.get_path(url_req)
        hostname = url_req.hostname
        query = self.get_query(url_req)
        port = self.get_port(url_req)
        post_body = ""

        if args != None:
            post_body = urllib.parse.urlencode(args)
        
        content_length = len(post_body)
        payload = f"POST {path}{query} HTTP/1.1\r\nHost: {hostname}\r\nUser-Agent: Mozilla/5.0\r\n"
        payload += f"Content-Type: application/x-www-form-urlencoded\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n"
        payload += post_body +"\r\n\r\n"
        
        # send and receive the data from the host
        code,body = self.send_receive(hostname, port, payload)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"

    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
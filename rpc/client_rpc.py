#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import struct
import socket

# sock.recv() 防止读阻塞方法
def receive(sock, n):
    rs = []  # 读取的结果
    while n > 0:
        r = sock.recv(n).decode('utf-8') #byte转str
        if not r:  # EOF
            return rs
        rs.append(r)
        n -= len(r)
    return ''.join(rs).encode('utf-8')  #str转byte

def rpc(sock, in_, params):
    request = json.dumps({"in": in_, "params": params})  # 请求消息体
    length_prefix = struct.pack("I", len(request)) # 请求长度前缀
    sock.sendall(length_prefix)
    # sock.sendall(request) python3 报错，TypeError: a bytes-like object is required, not 'str'，sendall()方法str需要转为bytes，读取时用decode('utf-8'),修改如下
    sock.sendall(request.encode('utf-8'))
    length_prefix = receive(sock, 4)  # 响应长度前缀 sock.recv(4) 防止阻塞改写
    length, = struct.unpack("I", length_prefix)
    body = receive(sock, length) # 响应消息体
    response = json.loads(body)
    return response["out"], response["result"]  # 返回响应类型和结果

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8080))
    for i in range(10): # 连续发送 10 个 rpc 请求
        out, result = rpc(s, "ping", "ireader %d" % i)
        print(out, result)
        time.sleep(1)  # 休眠 1s，便于观察
    s.close() # 关闭连接


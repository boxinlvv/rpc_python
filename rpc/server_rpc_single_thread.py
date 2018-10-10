#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
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

def handle_conn(conn, addr, handlers):
    print(addr, "comes")
    while True:  # 循环读写
        length_prefix = receive(conn, 4)  # 请求长度前缀
        if not length_prefix:  # 连接关闭了
            print(addr, "bye")
            conn.close()
            break  # 退出循环，处理下一个连接
        length, = struct.unpack("I", length_prefix)
        body = receive(conn, length)  # 请求消息体  
        request = json.loads(body)
        in_ = request['in']
        params = request['params']
        print(in_, params)
        handler = handlers[in_]  # 查找请求处理器
        handler(conn, params)  # 处理请求


def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()  # 接收连接
        handle_conn(conn, addr, handlers)  # 处理连接


def ping(conn, params):
    send_result(conn, "pong", params)


def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result})  # 响应消息体
    length_prefix = struct.pack("I", len(response))  # 响应长度前缀
    conn.sendall(length_prefix)
    conn.sendall(response.encode('utf-8'))


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建一个 TCP 套接字
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 打开 reuse addr 选项
    sock.bind(("localhost", 8080)) # 绑定端口
    print('Server localhost:80000...')
    sock.listen(1)  # 监听客户端连接
    handlers = {  # 注册请求处理器
        "ping": ping
    }
    loop(sock, handlers)  # 进入服务循环
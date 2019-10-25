'''
请求协议登录 L
    　 注册 R
       退出 Q
       查找　F
       历史　H
'''
import socket
import os, sys
import getpass
import hashlib
import datetime

U = ('127.0.0.1', 8080)


class Send:
    def __init__(self, sockfd):
        self.sockfd = sockfd
        self.name = None
    #登录成功后才会调用这个函数
    def do_select_word_history(self):
        """

        :return:None
        """
        while True:
            print('-------------')
            print('--查询单词(f)')
            print('--查询历史(h)')
            print('--退出登录(Q)--')
            print('-------------')
            word = input('输入你需要功能(f/h)')
            if word == 'f':
                self.do_select_word()
            elif word == 'h':
                self.do_select_history()
            elif word == 'Q':
                self.do_quit()
            else:
                continue

    def do_select_word(self):
        """
        向服务器端发送查询单词的请求
        :return:None
        """
        data = input('--查找的单词:--')
        self.sockfd.send(('F ' + str([self.name, data])).encode())
        new_data = self.sockfd.recv(2048).decode()
        print(new_data)
        return

    def do_select_history(self):
        """
        向服务器端发送查询历史记录的请求
        :return: none
        """
        self.sockfd.send(('H ' + self.name).encode())
        data = self.sockfd.recv(2048).decode()
        #注意eval　因为客户端发送过来的是str(元祖)元祖里面还有
        #datetime这个时间记录所以需要调用datetime这个包
        for i in eval(data):
            print(i)
        return

    def do_register(self):
        """
        注意密码加密gpasswd和hashlib的调用
        :return:
        """
        while True:
            print('请输入用户名和密码')
            name = input('请输入新建用户名')
            #密码加密
            passwd = getpass.getpass('请输入新建密码')
            hash1 = hashlib.md5(b'salt')#加盐处理
            hash1.update(passwd.encode())
            passwd = hash1.hexdigest()


            self.sockfd.send(('R ' + str([name, passwd])).encode())
            data = self.sockfd.recv(1024).decode()
            if data == '用户存在重新输入' or '注册失败':
                print(data)
                return
            return

    def do_login(self):
        """
                注意密码加密gpasswd和hashlib的调用
                :return:
        """
        while True:
            print('请输入用户名和密码')
            name = input('请输入用户名')

            #密码加密
            passwd = getpass.getpass('请输入密码')
            hash1 = hashlib.md5(b'salt')
            hash1.update(passwd.encode())
            passwd = hash1.hexdigest()


            self.sockfd.send(('L ' + str([name, passwd])).encode())
            data = self.sockfd.recv(1024).decode()
            if data == '登录成功':
                self.name = name
                print(data)
                self.do_select_word_history()
            print(data)
            return

    def do_quit(self):
        self.sockfd.send(b"Q print('bye')")
        data = self.sockfd.recv(128).decode()
        if data:
            print(data)
            self.sockfd.close()
            sys.exit('退出')


def main():
    s = socket.socket()
    s.connect(U)
    send_to = Send(s)

    while True:
        print('--欢迎进入电子词典--')
        print('-----登录(1)-----')
        print('-----注册(2)-----')
        print('-----退出程序(Q)---')
        data = input('请输入')
        if data == '1':
            send_to.do_login()
            pass

        if data == '2':
            send_to.do_register()
            pass
        if data == 'Q':
            send_to.do_quit()
            return
        else:
            print('请正确操作')
            continue


main()

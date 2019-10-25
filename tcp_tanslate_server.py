import pymysql
import socket
import signal
import os, sys
import multiprocessing
import datetime

U = ('0.0.0.0', 8080)


class Database:
    def __init__(self, host='localhost',
                 port=3306,
                 user='root',
                 passwd='123456',
                 database='dict',
                 charset='utf8'):
        self.db = pymysql.connect(host='localhost',
                                  port=3306,
                                  user='root',
                                  passwd='123456',
                                  database='dict',
                                  charset='utf8')
        self.host = host
        self.user = user
        self.port = port
        self.passwd = passwd
        self.database = database
        self.charset = charset
        self.login_L = None

        self.cur = self.db.cursor()

    def close(self):
        if self.cur:
            self.cur.close()
        self.db.close()

    def register(self, name, passwd):
        """

        :param name:客户端发送的需要注册的用户名
        :param passwd: 客户端发送来的需要注册的密码
        :return: 注册成功或者失败的结果
        """
        sql = "select name from user where name = %s;"
        insert_sql = "insert into user (name,passwd) values (%s,%s)"
        self.cur.execute(sql, [name])
        result = self.cur.fetchall()
        if result:
            return '用户存在重新输入'
        try:
            self.cur.execute(insert_sql, [name, passwd])
            self.db.commit()
            return '注册成功'

        except Exception as e:

            print(e)
            self.db.rollback()
            return '注册失败'

    def login(self, name, passwd):
        """
        :param name: 客户端发送来的用户名
        :param passwd: 客户端发送来的用户名密码
        :return:登录的结果
        """
        sql = 'select name,passwd from user where name=%s'
        try:
            self.cur.execute(sql, [name])
            for item in self.cur.fetchall():
                if name == item[0] and passwd == item[1]:
                    return '登录成功'
            else:
                return '登录失败(请输入正确的帐号密码)'
        except Exception:

            return '登录失败系统故障'

    def select_word(self, name, word):
        """

        :param name: 请求查询单词的用户
        :param word: 需要查询的单词
        :return: 查询结果
        """
        sql = 'select word,mean from words where word = %s;'
        try:
            self.cur.execute(sql, [word])
            data_1 = self.cur.fetchone()
            #查一条单词讲用户名和单词写入历史记录表
            self.into_history(name, word)
            if data_1:
                return str(data_1)
        except Exception:
            return '没有此单词'
        return '没有%s请确认'%word
    def into_history(self, name, word):
        """

        :param name: 需要写入历史记录表的用户名
        :param word: 写入历史记录表的单词
        :return: None
        """
        sql_1 = 'insert into history (name,word) values (%s,%s)'
        try:
            self.cur.execute(sql_1, [name, word])
            self.db.commit()
        except Exception as e:
            print(e)

    def select_history(self, name):
        """

        :param name:服务端发送的用户名
        :return: 查寻历史记录表的前10条记录的结果
        """
        sql_1 = 'select name,word,time from history ' \
                'where name = %s order by time desc limit 10'
        try:
            self.cur.execute(sql_1, [name])
            self.db.commit()
            return self.cur.fetchall()
        except Exception as e:
            print(e)

    def quit_(self, addr, c):
        #判断客户端退出，将C套接字关闭
        c.send(b'Thanks Bye')
        c.close()
        self.close()
        print(addr,'退出')


#接受请求处理请求的逻辑
def quest_target(target, c, addr):
    while True:
        try:
            """
            R:注册协议
            L:登录协议
            Q:退出协议
            F:查询单词协议
            H:查询历史记录协议
            """
            data = c.recv(128).decode().split(' ', 1)  # data[0]协议[1]内容
            if not data:
                c.close()
                return
            #因为只能通过二进制发送所以接受到的消息是str所以数据结构是'R [data,data]'所以切割
            #然后用eval函数得到一个[data,data]的列表
            elif data[0] == 'R':
                need_data = eval(data[1])
                target_send = \
                    target.register(need_data[0], need_data[1])
                c.send(target_send.encode())
            elif data[0] == 'L':
                need_data = eval(data[1])
                target_send = \
                    target.login(need_data[0], need_data[1])  # 0和1分别对应用户名密码
                c.send(target_send.encode())
                continue
            elif data[0] == 'Q':
                target.quit_(addr, c)
            elif data[0] == 'F':
                need_data = eval(data[1])
                target_send = target.select_word(need_data[0], need_data[1])
                c.send(target_send.encode())
            elif data[0] == 'H':
                target_send = str(target.select_history(data[1]))
                c.send(target_send.encode())

        except Exception:
            return

#程序主体结构
def main():
    # 服务器创建套接字
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(U)
    s.listen(8)

    # 采用多进程防止僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    jobs = []

    #循环接受客户端请求,通过Database创建不同的实例，进行操作
    while True:
        try:
            target = Database()
            c, addr = s.accept()
            print('connet from...', addr)
            p1 = multiprocessing.Process(target=quest_target, args=(target, c, addr))
            p1.start()
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务端退出')
        except Exception as e:
            print(e)
            continue
    for i in jobs:
        i.join()

#如果是windows用户 运行main时候一定要加if __name__ == '__main__',因为windows操作进程有保护机制.防止递归创建进程
main()

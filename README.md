# Logic_python
基于python的小算法,小项目
分为服务端和客户端
协议:
Q(退出协议客户端发送Q协议)
L(登录协议)
R(注册协议)
F(查找协议)
H(查找历史记录协议)
当有一个客户端连接时候服务端会开一个进程进行与客户端交互
win用户:1无法使用signal信号处理僵尸进程建议写一个类似signal信号处理逻辑的装饰器
       ２父进程的创建的游标实例无法传递给子进程建议用线程(注意一下用锁防止对游标的争夺，导致数据库数据混乱)
       ３如果用进程处理并发那么一定不要想着父进程创建IO实例对象传递给子进程!无法传递!!!一定要在每个子进程下创建!

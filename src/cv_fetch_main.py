from gevent import monkey;

monkey.patch_os()
from gevent.server import StreamServer
from multiprocessing import Process
from multiprocessing import cpu_count

import os
from liepin import process_liepin
from zhilian import process_zhilian
import chardet
from qiancheng import process_qiancheng

from logger import FetchLogger

max_buffer_size = 8192
default_port = 8090

sep = "\n\n"
from urllib import unquote


def cb(socket, address):
    log = FetchLogger().getLogger()
    log.fatal("remote address:%s" % (str(address)))
    #     send_msg(socket, "jwm:to:"+str(address)+str(socket))
    #     return
    rev = socket.recv(max_buffer_size)
    log.fatal("len(rev):%s" % len(rev))

    parts = rev.split("\r\n\r\n")
    log.fatal("len(parts):%d" % (len(parts)))
    for p in parts:
        print "===>", p, "<===="

    if len(parts) != 2:
        send_msg(socket, "1" + sep + "requests error.")
        return

    for ix in range(2):
        parts[ix] = unquote(parts[ix])
        det_code = chardet.detect(parts[ix])
        encoding = det_code["encoding"]
        if None == encoding or encoding == "utf-8":
            pass
        else:
            parts[ix] = parts[ix].decode(encoding).encode("utf-8")

    query = parts[0].split("\r\n")[0][7:-9]
    log.fatal("query:" + query)
    log.fatal("payload:" + parts[1])

    query_maps = {}
    for elem in query.split("&"):
        kv = elem.split("=")
        query_maps[kv[0]] = kv[1]

    if not (query_maps.has_key("site_type")
            and query_maps.has_key("user")
            and query_maps.has_key("passwd")
            and query_maps.has_key("op_type")):
        send_msg(socket, "1" + sep + "requests parameter wrong.")
        return

    payload = {}
    if parts[1] and len(parts[1]) > 0:
        for elem in parts[1].split("&"):
            kv = elem.split("=")
            payload[kv[0]] = kv[1]

    site_type = query_maps["site_type"]
    if site_type == "1":
        ret = process_liepin(query_maps, payload)
    elif site_type == "2":
        ret = process_zhilian(query_maps, payload)
    elif site_type == "3":
        ret = process_qiancheng(query_maps, payload)
    else:
        ret = "1" + sep + "not supported site_type:%s" % (site_type)
    send_msg(socket, ret)


def send_msg(socket, msg):
    ret = 'HTTP/1.1 200 OK\n\n' + msg
    socket.sendall(ret.encode("utf-8"))
    socket.close()


def start_server(nr_proc=1, port=8080):
    log = FetchLogger().getLogger()
    cpu_cnt = cpu_count()
    nr_proc = nr_proc if nr_proc < cpu_cnt else cpu_cnt

    if os.name == "nt":
        nr_proc = 1  # ONLY 1 process supported in windows.

    server = StreamServer(('', port), cb, backlog=100000)
    server.start()

    def serve_forever():
        server.start_accepting()
        log.fatal("start listening in port:%d" % port)
        server.serve_forever()
        log.fatal("Done")

    for _ in range(nr_proc - 1):
        Process(target=serve_forever, args=tuple()).start()
    serve_forever()


def use_help():
    print """usage: python main.py [port]
           default port:8090
           
as a daemon: python main.py [port]&
eg: python main 8081 &"""


if __name__ == "__main__":
    log = FetchLogger().getLogger()
    log.fatal("os.name:%s" % os.name)
    import sys

    log.fatal(str(sys.argv))
    if len(sys.argv) > 2:
        help()
        sys.exit(1)
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except:
            use_help()
            sys.exit()
    else:
        port = default_port

    pid = str(os.getpid())
    log.fatal("pid:%s" % pid)
    with open("pid.txt", "w") as f:
        f.write(pid)

    start_server(port=port)

#!/usr/bin/env python3
# coding: utf-8
#authour lizili
import sys
import requests

CREATE_GRAPH_URL=r"http://ipaddr:8000/wechat/create_graph/"

try:
    msg_argv=sys.argv[3].split("&&")
    create_url="%s?itemid=%s&eventid=%s-%s.png"%(CREATE_GRAPH_URL,msg_argv[9],msg_argv[0],msg_argv[2])
    req=requests.post(create_url,timeout=6)
    print(req.status_code)
    if(req.text!="ok"):
        exit(0)
except Exception as exc:
    print(exc.args)
    exit(1)

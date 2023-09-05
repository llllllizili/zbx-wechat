#!/usr/bin/env python3
# coding: utf-8
#authour lizili
import sys
import requests
from time import sleep
import json
import time

WX_CORPID = r"wx6f8xxxxxxxxx7"
WX_CORPSECRET = r"QbsogAeKZGg_NsNu2xxxxxxxxxqBTImxxxxxxxxxi2dsRs"
AGENT_ID = '1'
#TOPARTY='8'

CALLBACK_URL="italert.xxxxxxxxx.com:25073"
CALLBACK_ACK_URL="http://%s/wechat/ack/"%CALLBACK_URL
CALLBACK_DETIAL_URL="http://%s/wechat/detial/"%CALLBACK_URL

GRAPH_URL="http://%s/static/images/graph/"%CALLBACK_URL
ICON_URL="http://%s/static/images/icon/"%CALLBACK_URL

WX_TOKEN_FILE = "/tmp/wechat_accesstoken_zabbix_wechat"
LOG_FILE="/tmp/zabbix_send_log"



def c_log(msg):
	try:
		perameter_file=open(LOG_FILE,'a')
		perameter_file.write(msg+"\n")
	except:
		exit(1)
	finally:
		perameter_file.close()

def refresh_token(corpid=WX_CORPID, corpsecrt=WX_CORPSECRET):
    get_url = r"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + WX_CORPID + "&corpsecret=" + WX_CORPSECRET
    for i in range(3):
        try:
            req_ret = requests.get(get_url, timeout=6)
            jso_ret = req_ret.json()
            file_tok = open(WX_TOKEN_FILE, "w")
            file_tok.write(jso_ret["access_token"])
            file_tok.close()
            return jso_ret["access_token"]
        except requests.exceptions.ConnectTimeout:
            sleep(10)
        except Exception as exc:
            print(exc.args)
            return None
    return None

def get_token(corpid=WX_CORPID, corpsecrt=WX_CORPSECRET):
    try:
        file_tok = open(WX_TOKEN_FILE, "r")
        token = file_tok.read()
        file_tok.close()
        if len(token) !=64:
            raise FileNotFoundError(r"token length !=64")
        return token
    except FileNotFoundError:
        get_url = r"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + WX_CORPID + "&corpsecret=" + WX_CORPSECRET
        for i in range(3):
            try:
              req_ret = requests.get(get_url, timeout=6)
              jso_ret = req_ret.json()
              file_tok = open(WX_TOKEN_FILE, "w")
              file_tok.write(jso_ret["access_token"])
              file_tok.close()
              return jso_ret["access_token"]
            except requests.exceptions.ConnectTimeout:
                sleep(10)
            except Exception as exc:
                print(exc.args)
                return None
    except Exception as exc:
            print(exc.args)
    return None

def create_articles():
    msg_argv=sys.argv[3].split("&&")
    if(msg_argv[0]=="PROBLEM"):
        if(msg_argv[1]=="灾难"):
            level_img="zn.png"
        elif(msg_argv[1]=="一般严重"):
            level_img="yb.png"
        elif(msg_argv[1]=="严重"):
            level_img="yz.png"
        elif(msg_argv[1]=="警告"):
            level_img="jg.png"
        elif(msg_argv[1]=="通知"):
            level_img="tz.png"
        else:
            level_img="wfl.png"
        ret = [
            {
                "title": "%s"%(msg_argv[10]),
                #"description":"ID:%s\n告警时间: %s"%(msg_argv[3],msg_argv[7]),
				"url": "%s%s-%s.png"%(GRAPH_URL,msg_argv[0],msg_argv[2]),
                "picurl": "%s%s-%s.png"%(GRAPH_URL,msg_argv[0],msg_argv[2]),
				#"picurl": "%s%s-%s.png"%('/home/ubuntu/django/wechat/zbx/static/images/graph/',msg_argv[0],msg_argv[3]),
			},
            {
                "title":"主机名称: %s \n所属主机: %s"%(msg_argv[4],msg_argv[5]),
                #"picurl": "%s"%(pic_url),
            },
            {
                #"title":"ID: %s\n告警描述:\n%s"%(msg_argv[3],msg_argv[8]),
				"title":"ID: %s\n点击查看更多"%(msg_argv[2]),
                "url": "%s?event_name=%s&host_group=%s&host_name=%s&host_ip=%s&event_time=%s-%s&desc=%s&severity=%s"%(CALLBACK_DETIAL_URL,msg_argv[10],msg_argv[3],msg_argv[4],msg_argv[5],msg_argv[6],msg_argv[7],msg_argv[8],msg_argv[1]),
            },
			{
                #"title":"确认告警(负责人点击)\nID:%s"%(msg_argv[3]),
                "title":"确认告警\n(负责人点此响应告警)",
				"url": "%s?event_id=%s&from_user=%s&event_name=%s&host_group=%s&host_name=%s&host_ip=%s"%(CALLBACK_ACK_URL,msg_argv[2],sys.argv[1],msg_argv[10],msg_argv[3],msg_argv[4],msg_argv[5]),
				"picurl": "%s%s"%(ICON_URL,level_img),
				#"picurl": "%stest.jpg"%(ICON_URL),
            }
        ]
        return ret
    elif(msg_argv[0]=="OK"):
        if(msg_argv[1]=="通知"):
            return None
        else:
            level_img="hf.png"
            return [
                {
                "title": "恢复-%s"%(msg_argv[10]),
                "url": "%s%s-%s.png"%(GRAPH_URL,msg_argv[0],msg_argv[2]),
                "picurl": "%s%s-%s.png"%(GRAPH_URL,msg_argv[0],msg_argv[2]),
                },
                {
                "title":"主机名称: %s\n主机地址: %s"%(msg_argv[4],msg_argv[5]),
                #"picurl": "%s"%pic_url
                },
                {
                "title":"持续时长：%s\n告警时间: %s-%s"%(msg_argv[11],msg_argv[6],msg_argv[7]),
                },
                {
                "title":"ID: %s\n点击查看更多"%(msg_argv[2]),
                "url": "%s?event_name=%s&host_group=%s&host_name=%s&host_ip=%s&event_time=%s-%s&desc=%s&severity=%s"%(CALLBACK_DETIAL_URL,msg_argv[10],msg_argv[3],msg_argv[4],msg_argv[5],msg_argv[12],msg_argv[13],msg_argv[8],msg_argv[1]),
                "picurl": "%s%s"%(ICON_URL,level_img),
                }
            ]
    return None

def send_news(type,target,arti):
#def send_news(arti):
    access_token = get_token()
    if access_token == None:
        return 1
    send_msg_url = r"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+access_token
    msg_josn ={}
    if(type==0):
        msg_josn["touser"] = target
    elif(type==1):
        msg_josn["toparty"] = target
    else:
        return 1
    msg_josn["msgtype"] = "news"
    msg_josn["agentid"] = AGENT_ID

    msg_josn["news"] = {"articles": arti}
    #print (msg_josn)
    send_data = json.dumps(msg_josn, ensure_ascii=False).encode(encoding='UTF8',)
    #print(send_data)
    for i in range(4):
        try:
            if i >= 4:
                return 1
            req_ret = requests.post(send_msg_url, data=send_data, timeout=5)
            c_log(req_ret.text)
            jos_ret = req_ret.json()

            if jos_ret["errcode"] == 0:
                return 0
            elif jos_ret["errcode"] == 40014:
                token = refresh_token(WX_CORPID, WX_CORPSECRET)
                if token == None:
                    return 1
                access_token = token
                send_msg_url = r"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
            else:
                return 1
        except requests.exceptions.ConnectTimeout:
            sleep(2)
        except Exception as exc:
            return 1
    return 1

if __name__=="__main__":
    articles=create_articles()
    if(articles==None):
        exit(1)
    if(send_news(0,sys.argv[1],articles)!=0):
        exit(1)

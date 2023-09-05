#!/usr/bin/env python3
# coding: utf-8
#authour lizili
import sys
import requests
from time import sleep
import json
import time

class WeiXin():
    WX_CORPID = r"wx643fxxxxxxxxxxxx"
    WX_CORPSECRET = r"QbsxxxxGg_NsNu2txxxxxxxxxxxxTImc32dsRs"
    AGENT_ID = '1'
    #TOPARTY='8'


    CALLBACK_URL="italert.xxxxxxxxxxxx.com:22222"
    CALLBACK_ACK_URL="http://%s/wechat/ack/"%CALLBACK_URL

    GRAPH_URL="http://%s/static/images/graph/"%CALLBACK_URL
    ICON_URL="http://%s/static/images/icon/"%CALLBACK_URL

    LOG_FILE="/tmp/zabbix_send_log"
    WX_TOKEN_FILE = "/tmp/wechat_accesstoken_zabbix_weixin"

    def __init__(self):
        pass

    def c_log(self,msg):
        try:
            perameter_file=open(self.LOG_FILE,'a')
            perameter_file.write(msg+"\n")
        except:
            exit(1)
        finally:
            perameter_file.close()

    def refresh_token(self,corpid=WX_CORPID, corpsecrt=WX_CORPSECRET):
        get_url = r"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + self.WX_CORPID + "&corpsecret=" + self.WX_CORPSECRET
        for i in range(3):
            try:
                req_ret = requests.get(get_url, timeout=6)
                jso_ret = req_ret.json()
                file_tok = open(self.WX_TOKEN_FILE, "w")
                file_tok.write(jso_ret["access_token"])
                file_tok.close()
                return jso_ret["access_token"]
            except requests.exceptions.ConnectTimeout:
                sleep(10)
            except Exception as exc:
                print(exc.args)
                return None
        return None

    def get_token(self,corpid=WX_CORPID, corpsecrt=WX_CORPSECRET):
        try:
            file_tok = open(self.WX_TOKEN_FILE, "r")
            token = file_tok.read()
            file_tok.close()
            if len(token) !=64:
                raise FileNotFoundError(r"token length !=64")
            return token
        except FileNotFoundError:
            get_url = r"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + self.WX_CORPID + "&corpsecret=" + self.WX_CORPSECRET
            for i in range(3):
                try:
                  req_ret = requests.get(get_url, timeout=6)
                  jso_ret = req_ret.json()
                  file_tok = open(self.WX_TOKEN_FILE, "w")
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

    def send_news(self,type,target,arti):
    #def send_news(arti):
        access_token = self.get_token()
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
        msg_josn["agentid"] = self.AGENT_ID

        msg_josn["news"] = {"articles": arti}
        print (msg_josn)
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
                    token = refresh_token(self.WX_CORPID, self.WX_CORPSECRET)
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

    def send_text(self,type,target,arti):
        access_token=self.get_token()

        if access_token == None:
            return 1
        send_msg_url = r"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+access_token
        msg_josn = {}
        if(type==0):
            msg_josn["touser"] = target
        elif(type==1):
            msg_josn["toparty"] = target
        else:
            return 1
        msg_josn["msgtype"] = "text"
        msg_josn["agentid"] = self.AGENT_ID

        msg_josn["text"] = {
            "content": arti
        }
        send_data = json.dumps(msg_josn, ensure_ascii=False).encode(encoding='UTF8', )

        for i in range(4):
            try:
                if i >= 4:
                    return 1
                req_ret = requests.post(send_msg_url, data=send_data, timeout=5)
                print(req_ret.text)
                self.c_log(req_ret.text)
                jos_ret = req_ret.json()

                if jos_ret["errcode"] == 0:
                    return 0
                elif jos_ret["errcode"] == 40014:
                    token = self.refresh_token(self.WX_CORPID, self.WX_CORPSECRET)
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

    def get_userid(self,code):
        access_token=self.get_token()
        if(access_token==None):
            return 1
        for i in range(2):
            req_url="https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token=%s&code=%s"%(access_token,code)
            try:
                req=requests.get(req_url,timeout=6)
                req_jso=req.json()
                if("UserId" in req_jso.keys()):
                    return (req_jso["UserId"])
                elif("errcode" in req_jso.keys()):
                    if(req_jso["errcode"]==40014):
                        access_token=self.refresh_token()
                        continue
                else:
                    return 1
            except Exception as exc:
                return 1
        return 1


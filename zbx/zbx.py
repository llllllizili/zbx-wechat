import requests
import json
import urllib.request
import http.cookiejar
import time

class Zbx:
    auth=None
    zbx_host='ipaddr'
    login_url="http://%s/monitor/index.php"%zbx_host
    api_url="http://%s/monitor/api_jsonrpc.php"%zbx_host

    __api_user="api_user"
    __api_password="api_user"

    admin_users=[]
    #实例化类需要用户名和密码两个参数，默认api_user,api_user
    def __init__(self,user=__api_user,password=__api_password):
        self.user=user
        self.password=password
    #通过api，提取auth
    def login(self):
        data = {"jsonrpc":"2.0","method":"user.login","params":{"user":self.user,"password":self.password},"id":0}
        headers={"Content-Type": "application/json"}
        try:
            req = requests.post(self.api_url,data=json.dumps(data),headers=headers,timeout=3)
            self.auth = req.json()["result"]
            #print(self.auth)
            return self.auth
        except Exception as exc:
            print(exc.args)
        print("Get auth error")
        return 1
    #通过api确认告警
    def ack_event(self,eventid):
        self.login()
        data = {"jsonrpc": "2.0","method": "event.acknowledge","params":
        {"eventids": eventid,"message": "%s 通过微信确认"%self.user,"action": 0},
            "auth": self.auth,
            "id": 1
        }
        headers={"Content-Type": "application/json"}
        try:
            req = requests.post(self.api_url,data=json.dumps(data),headers=headers,timeout=3)
            #print(req.json()["result"]["eventids"][0])
            return req.json()["result"]["eventids"][0]
        except Exception as exc:
            print(exc.args)
        return 1

    #获取用户组内 用户信息
    def get_group_user_info(self,groupname):
        self.login()
        data = {
            "jsonrpc": "2.0",
            "method": "usergroup.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": groupname
                },
                "selectUsers":["userid","alias","name","surname"],
                "status": 0
            },
            "auth": self.auth,
            "id": 1
        }
        try:
            req = requests.post(self.api_url, data=json.dumps(data), headers={"Content-Type": "application/json-rpc"},
                                timeout=5)
            req_jso=req.json()
            if(req_jso["result"].__len__()==0):
                return 1
            users_info=[]
            for i in req_jso["result"][0]["users"]:
                users_info.append([i["userid"],i["alias"],i["name"],i["surname"]])
            return users_info
            return req.json()["result"]["eventids"]
        except Exception as exc:
            return 1
        return 1

    #获取管理员信息
    def init_admin_users(self):
        self.login()
        user_infos=self.get_group_user_info("管理员组")
        if(user_infos==1):
            return
        for i in user_infos:
            self.admin_users.append(i[1])
    #获取相关组内成员信息
    def get_noti_users(self,host_group):
        self.login()
        user_info_list=self.get_group_user_info(host_group)
        if(user_info_list==1):
            return self.admin_users
        user_list=[]
        for i in user_info_list:
            user_list.append(i[1])
        return user_list+self.admin_users
    #获取告警确认人
    def get_ack_user(self,eventid):
        data= {
            "jsonrpc": "2.0",
            "method": "event.get",
            "params": {
                "output": "acknowledgeid",
                "eventids": eventid,
                "select_acknowledges": "extend",
                "selectTags": "extend",
            },
            "auth": self.auth,
            "id": 1
        }
        try:
            req=requests.post(self.api_url,data=json.dumps(data),headers={"Content-Type": "application/json-rpc"},timeout=3)
            req_json=req.json()
            u_list=[]
            for i in req_json["result"]:
                u_l = i['acknowledges'][0]['name']

                u_list.append(u_l)
            return u_list
        except:
            e = ['无']
            return e
        return "get ack_user error"

    def for_ack_user(self):
        weijiechu_list=self.get_alarm_list(1)
        ack_u = []
        i = 0
        while i < len(weijiechu_list):
            a = self.get_ack_user(weijiechu_list[i][0])
            ack_u.append(a)
            i += 1
        return ack_u
        #获取告警列表
    def get_alarm_list(self,type=0):
        self.login()
        if(type==0):
            data = {
                "jsonrpc": "2.0",
                "method": "trigger.get",
                "params": {
                    "output": ["description","priority","comments"],
                    "filter": {
                        "value": 1
                    },
                    "selectHosts": ["name"],
                    "withLastEventUnacknowledged":"1",
                    "selectGroups": ["name"],
                    "selectItems": ["name"],
                    "selectLastEvent":["eventid","clock","acknowledged"],
                    "sortfield": "priority"
                },
                "auth": self.auth,
                "id": 1
            }
        elif(type==1):
            data = {
                "jsonrpc": "2.0",
                "method": "trigger.get",
                "params": {
                    "output": ["description", "priority", "comments"],
                    "filter": {
                        "value": 1
                    },
                    "selectHosts": ["name"],
                    "selectGroups": ["name"],
                    "selectItems": ["name"],
                    "selectLastEvent": ["eventid", "clock","acknowledged"],
                    "sortfield": "priority"
                },
                "auth": self.auth,
                "id": 1
            }
        else:
            return 1
        try:
            req = requests.post(self.api_url, data=json.dumps(data), headers={"Content-Type": "application/json-rpc"},timeout=5)
            req_jso=req.json()
            weiqueren_list=[]
            for p in req_jso["result"]:
                general_time=time.strftime("%m-%d %H:%M",time.localtime(int(p["lastEvent"]["clock"])))
                eventid=p["lastEvent"]["eventid"]
                host_info="%s->%s->%s"%(p["groups"][0]["name"],p["hosts"][0]["name"],p["description"])
                hostname=p["hosts"][0]["name"]
                comments=p["comments"]
                item=p["items"][0]["name"]
                description=p["description"]
                if(p["priority"]=="0"):
                    priority="未分类"
                elif(p["priority"]=="1"):
                    priority="通知"
                elif(p["priority"]=="2"):
                    priority="警告"
                elif(p["priority"]=="3"):
                    priority="一般"
                elif(p["priority"]=="4"):
                    priority="严重"
                elif(p["priority"]=="5"):
                    priority="灾难"
                if(p["lastEvent"]["acknowledged"]=="0"):
                    is_ack="未确认"
                elif(p["lastEvent"]["acknowledged"]=="1"):
                    is_ack="已确认"
                else:
                    is_ack="未知"
                weiqueren_list.append([eventid,priority,host_info,comments,is_ack,general_time,item,hostname,description])

            return weiqueren_list
        except Exception as exc:
            print(exc.args)
        return 1



    def batch_ack(self,ack_list):
        data = {
            "jsonrpc": "2.0",
            "method": "event.acknowledge",
            "params": {
                "eventids": ack_list,
                "message": "%s 通过微信确认" % self.user,
                "action": 0
            },
            "auth": self.auth,
            "id": 1
        }
        try:
            req = requests.post(self.api_url, data=json.dumps(data), headers={"Content-Type": "application/json-rpc"},
                                timeout=5)
            return req.json()["result"]["eventids"]
        except Exception as exc:
            return 1
        return 1

    def get_user_hostgroups(self,username):
        data = {
            "jsonrpc": "2.0",
            "method": "user.get",
            "params": {
                "output": ["userid","alias","name"],
                "filter":{
        	        "alias":username
                },
                "selectUsrgrps":["usergroupid","name"]
            },
            "auth": self.auth,
            "id": 1
        }
        try:
            req = requests.post(self.api_url, data=json.dumps(data), headers={"Content-Type": "application/json-rpc"},
                                timeout=5)
            req_jso = req.json()
            if (req_jso["result"].__len__() == 0):
                return 1
            groups = []
            for i in req_jso["result"][0]["usrgrps"]:
                groups.append([i["usrgrpid"], i["name"]])

            return groups
        except Exception as exc:
            return 1
        return 1



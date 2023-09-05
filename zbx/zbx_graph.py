import requests
import json
import urllib.request
import http.cookiejar

class ZbxGraph:
    zabbix_host="ipaddress"
    login_url="http://%s/monitor/index.php"%zabbix_host
    graph2_url="http://%s/monitor/chart2.php"%zabbix_host
    api_url="http://%s/monitor/api_jsonrpc.php"%zabbix_host
    graph1_url="http://%s/monitor/chart.php"%zabbix_host

    api_user="api_user"
    api_password="api_user"
    auth=1
    def __init__(self):
        self.auth=self.__get_auth()
    def __del__(self):
        self.logout()
    def logout(self):
        if (self.auth==1):
            return 0
        data = {
            "jsonrpc": "2.0",
            "method": "user.logout",
            "params": {
            },
            "id": 1,
            "auth":self.auth
        }
        try:
            req = requests.post(self.api_url, data=json.dumps(data), headers={"Content-Type": "application/json-rpc"},timeout=3)
            self.auth=1
            return 0
        except Exception as exc:
            return 1
        return 1
    def __get_auth(self):
        data={
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": self.api_user,
            "password": self.api_password
        },
        "id": 1
    }
        try:
            req = requests.post(self.api_url, data=json.dumps(data), headers={"Content-Type": "application/json-rpc"},timeout=3)
            return req.json()["result"]
        except Exception as exc:
            print(exc.args)
        print("get auth error")
        return 1
    def get_graphid(self,itemid):
        data={
            "jsonrpc": "2.0",
            "method": "graphitem.get",
            "params": {
                "output":["graphid"],
                "expandData":1,
                "itemids":itemid
         },
        "auth":self.auth,
        "id": 1
    }
        try:
            req = requests.post(self.api_url, data=json.dumps(data), headers={"Content-Type": "application/json-rpc"},timeout=3)
            return req.json()["result"][0]["graphid"]
        except Exception as exc:
            return 1
        return 1
    def save_graph(self,graphid,file_name):
        login_data = urllib.parse.urlencode({
            "name": self.api_user,
            "password": self.api_password,
            "autologin": 1,
            "enter": "Sign in"
        }).encode()

        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)
        h = urllib.request.urlopen(self.login_url, login_data)

        graph_args = urllib.parse.urlencode({
            "graphid": graphid,
            "period":"3600",
            # "stime":'20171223210146', #图形开始时间
            # "updateProfile":'1',
            # "profileIdx":"web.screens",
            # "profileIdx2":"994",
            "width":"570"
        }).encode()

        try:
            req_data=opener.open(self.graph2_url,graph_args).read()
            print(file_name)
            file=open(file_name,"wb")
            file.write(req_data)
            file.flush()
            file.close()
            return 0
        except Exception as exc:
            print(exc.args)

        return 1

    def save_his_graph(self,itemid,file_name):
        login_data = urllib.parse.urlencode({
            "name": self.api_user,
            "password": self.api_password,
            "autologin": 1,
            "enter": "Sign in"
        }).encode()

        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)
        h = urllib.request.urlopen(self.login_url, login_data)

        graph_args = urllib.parse.urlencode({
            "itemids[0]": itemid,
            "period":"3600",
            # "stime":'20171223210146', #图形开始时间
            # "updateProfile":'1',
            # "profileIdx":"web.screens",
            # "profileIdx2":"994",
            "width": "570"
        }).encode()

        try:
            req_data = opener.open(self.graph1_url, graph_args).read()
            file = open(file_name, "wb")
            file.write(req_data)
            file.flush()
            file.close()
            return 0
        except Exception as exc:
            print(exc.args)

        return 1

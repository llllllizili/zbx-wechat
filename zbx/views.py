from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .zbx import Zbx
from .zbx_graph import ZbxGraph
from .weixin import WeiXin
from .WXBizMsgCrypt import WXBizMsgCrypt
import json


sToken = "W3ymWxxxxxxxxxxxx";
sCorpID = "wx643xxxxxxxxxxxx";
sEncodingAESKey = "ooWeM2xxxxxxxxxxxxRer5xxxxxxxxxxxx8Ks8kPP6CAOG";


last_ack_num=""
# Create your views here.

def test(request):
    a=request.GET['a']
    return render(request,'zbx/test.html',{'a':a})
def wxrz(request):
	return HttpResponse('IzaNHpJmAypFKZid')

@csrf_exempt
def wechat_callback(request):
    if(request.method=="POST"):
        return HttpResponse('<font size="18">暂不支持，请使用GET方式</font>')
    elif (request.method == "GET"):
        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
        # sVerifyMsgSig=HttpUtils.ParseUrl("msg_signature")
        sVerifyMsgSig = request.GET.get("msg_signature")
        # sVerifyTimeStamp=HttpUtils.ParseUrl("timestamp")
        sVerifyTimeStamp = request.GET.get("timestamp")
        # sVerifyNonce=HttpUitls.ParseUrl("nonce")
        sVerifyNonce = request.GET.get("nonce")
        # sVerifyEchoStr=HttpUtils.ParseUrl("echostr")
        sVerifyEchoStr = request.GET.get("echostr")
        ret, sEchoStr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
        if (ret != 0):
            return HttpResponse("error")
        else:
            return HttpResponse(sEchoStr)
@csrf_exempt
def ack(request):
    if request.method=='GET':
        event_id=request.GET['event_id']
        from_user=request.GET['from_user']
        event_name=request.GET['event_name']
        host_group=request.GET['host_group']
        host_name=request.GET['host_name']
        host_ip=request.GET['host_ip']

        global last_ack_num
        if(event_id==last_ack_num):
            return HttpResponse('<font size=18>该事件已确认,请勿重复请求</font>')
        last_ack_num=event_id
        ack = Zbx(from_user,from_user)
        if(ack.login()==1):
            return HttpResponse('<font size=18>登录失败</font>')
        if(ack.ack_event(event_id)==event_id):
            pass
        else:
            return HttpResponse('<font size=18>确认失败（过程失败）</font>')
        user_list=Zbx()
        user_list.login()
        noti_users=user_list.get_noti_users(host_group)
        wechat_noti_users=""
        for i in noti_users:
            wechat_noti_users="%s|%s"%(wechat_noti_users,i)
        wechat=WeiXin()
        #print(noti_users)
        if(0==wechat.send_text(0,wechat_noti_users,"---------告警处理通知---------\n此告警正在处理中.....\n责任人：%s\n事件ID：%s\n触发器：%s\n所属组：%s\n主机名：%s\n所属主机：%s"%(from_user,event_id,event_name,host_group,host_name,host_ip))):
            #print(noti_users)
            return HttpResponse('<font size="18">确认成功，请尽快处理告警</font>')
        else:
            #print(noti_users)
            return HttpResponse('<font size="18">确认成功（微信通知发送失败）</font>')
    return HttpResponse('<font size="18">请求失败</font>')

@csrf_exempt
def detial(request):
    if request.method=='GET':
        event_name=request.GET['event_name']
        host_group=request.GET['host_group']
        host_name=request.GET['host_name']
        host_ip=request.GET['host_ip']
        event_time=request.GET['event_time']
        desc=request.GET['desc']
        severity=request.GET['severity']

        return render(request,"zbx/detial.html",{"event_name":event_name,"host_group":host_group,"host_name":host_name,"host_ip":host_ip,"event_time":event_time,"desc":desc,"severity":severity,})

@csrf_exempt
def create_graph(request):
    if request.method=="POST":
        itemid=request.GET.get("itemid")
        eventid=request.GET.get("eventid")
        z=ZbxGraph()
        graphid=z.get_graphid(itemid)
        if(graphid==1):
            if(z.save_his_graph(itemid,"%s/zbx/static/images/graph/%s"%(settings.BASE_DIR,eventid))==0):
            #if(z.save_his_graph(itemid,"%s%s"%(ZBX_PIC_PATH,eventid))==0):
                return HttpResponse("ok")
        if(z.save_graph(graphid,"%s/zbx/static/images/graph/%s"%(settings.BASE_DIR, eventid))==0):
        #if(z.save_graph(graphid,"%s%s"%(ZBX_PIC_PATH,eventid))==0):
            return HttpResponse("ok")
    return HttpResponseBadRequest("error")

@csrf_exempt
def weiqueren(request):
    if request.method=="GET":
        code=request.GET.get("code")
        w=WeiXin()
        userid=w.get_userid(code)
        get_pro=Zbx(userid,userid)
        weiqueren_list=get_pro.get_alarm_list(0)
        if(weiqueren_list==1):
            return HttpResponse('<font size="18">获取列表失败（过程失败，请重新进入）!</font>')
        if(weiqueren_list.__len__()==0):
            title="您目前没有未确认告警"
        else:
            title="您有%s条未确认告警"%weiqueren_list.__len__()
        return render(request,"zbx/weiqueren.html",{"userid":userid,"title":title,"pro_list":weiqueren_list})
    else:
        return HttpResponse("error")
@csrf_exempt
def batch_ack(request):
    if request.method=="POST":
        ack_list=request.POST.getlist("ack_list")
        userid=request.POST.get("userid")
        if(ack_list.__len__()==0):
            return HttpResponse('<font size="18">确认列表为空</font>')
        ack_z=Zbx(userid,userid)
        if(ack_z.login()==1):
            return HttpResponse('<font size="18">确认失败（登陆失败）!</font>')
        ack_suc_list=ack_z.batch_ack(ack_list)
        if(ack_suc_list==1):
            return HttpResponse('<font size="18">批量确认失败（确认过程失败）!</font>')
        user_list = Zbx()
        user_list.login()
        groups=noti_gropus=user_list.get_user_hostgroups(userid)
        if(groups==1):
            return HttpResponse('<font size="18">确认成功（获取回执组失败！）!</font>')
        wechat_noti_users = ""
        for i in groups:
            noti_users = user_list.get_noti_users(i[1])
            for j in noti_users:
                wechat_noti_users="%s|%s"%(wechat_noti_users,j)
        ack_text = ""
        count = 0
        for i in ack_suc_list:
            count+=1
            ack_text+="事件%d-ID: %s\n"%(count,i)

        msg="-------告警批量处理通知-------\n以下告警正在处理中.....\n责任人：%s\n%s"%(userid,ack_text)
        w=WeiXin()
        if (0 == w.send_text(0, wechat_noti_users,msg)):
            return HttpResponse('<font size="18">批量确认成功,请尽快处理告警</font>')
        else:
            return HttpResponse('<font size="18">批量确认成功，但回执消息失败!</font>')
    return HttpResponseBadRequest("error")

@csrf_exempt
def weijiechu(request):
    if request.method=="GET":
        code=request.GET.get("code")
        w=WeiXin()
        userid=w.get_userid(code)
        z=Zbx(userid,userid)
        user_list=z.for_ack_user()
        weijiechu_list=z.get_alarm_list(1)
        info=list(zip(user_list,weijiechu_list))
        if(weijiechu_list==1):
            return HttpResponse('<font size="18">获取列表失败（过程失败，请重新进入）!</font>')
        if(weijiechu_list.__len__()==0):
            title="您目前没有未解除告警"
        else:
            title="您有%s条未解决告警"%weijiechu_list.__len__()
        return render(request,"zbx/weijiechu.html",{"userid":userid,"title":title,"pro_list":weijiechu_list,"user_list":user_list,"info":info})
    else:
        return HttpResponse("error")

@csrf_exempt
def search(request):
    if request.method=="GET":
        code=request.GET.get("code")
        w=WeiXin()
        userid=w.get_userid(code)
        return render(request,"zbx/search.html",{"userid":userid})
    else:
        return HttpResponse("error")

@csrf_exempt
def search_eventid(request):
    if request.method=="POST":
        return HttpResponse('<font size="18">开发中,敬请期待</font>')
        userid=request.POST.get("userid")
        eventid = request.POST.get("eventid")
        z=Zbx(userid,userid)








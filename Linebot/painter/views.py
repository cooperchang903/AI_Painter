from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,JsonResponse,FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from pathlib import Path
import json
import uuid

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

DefaultMessage ="AI Painter可以依您指定之主題(文字),自行產生特定風格之繪畫。請點選下方選單開始畫畫。\n如要取消請再點選下方Menu一次。"
PrompTextMessage="請以文字陳述想要繪畫的主題(中/英文皆可)"
bPrompInput = False

PaintData={
    "userid":"",
    "promptTxt":"",
    "uploadImages":[],
    "read":"N"
}

 
@csrf_exempt
def callback(request):
        global bPrompInput
        global PaintData
        image_url=[]
        print(f'===========>{bPrompInput}')
        if request.method == 'POST':
            message=[]
            signature = request.META['HTTP_X_LINE_SIGNATURE']
            body = request.body.decode('utf-8')
#             message.append(TextSendMessage(text=str(body)))
            
            try:
                events = parser.parse(body, signature)  
            except InvalidSignatureError:
                return HttpResponseForbidden()
            except LineBotApiError:
                return HttpResponseBadRequest()
#             print(f'Events:{events}')
           
            for event in events:

                if isinstance(event, MessageEvent):
#                     print(f'Message Type:{event.message.type}')
                    sender = event.source.sender_id
                    PaintData["userid"]=sender
#                     print(f'UserID:{sender}')
                    if event.message.type=='text':
                        if event.message.text=='Start Painting':
                            if(bPrompInput==True):
                                bPrompInput=False
                                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="已經取消繪畫動作"))
                            else:
                                bPrompInput=True
                                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=PrompTextMessage))
                            
                        else:
                            if(bPrompInput==True):
                                PaintData["promptTxt"]=event.message.text
                                message=TextSendMessage(
                                    text="請上傳風格圖片",
                                    quick_reply=QuickReply(
                                        items=[
                                            
                                            QuickReplyButton(
                                                action=CameraAction(label="拍照")
                                                ),
                                            QuickReplyButton(
                                                action=CameraRollAction(label="相簿")
                                                )
                                            ]
                                        )
                                )
                                
                                line_bot_api.reply_message(event.reply_token,message)
                           
                            else:
                                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=DefaultMessage))


                    elif event.message.type=='image':
                        if(bPrompInput==True):
                            #下載圖片檔案
                            message_id = event.message.id
                            message_content = line_bot_api.get_message_content(message_id)
                            
                            filePath = Path(f"Upload/{message_id}.jpg")
                            with open(filePath, 'wb') as f:
                                for chunk in message_content.iter_content():
                                    f.write(chunk)
                            
                            image_url.append(settings.SITE_URL+'images?id='+filePath.name)
                            PaintData["uploadImages"] = image_url
                            bPrompInput=False
                            
                            with open('Upload/ImageGen.json', 'w') as f:
                              json.dump(PaintData, f, ensure_ascii=False)
                            
                            message_text = f'您指定的主題:\n<{PaintData["promptTxt"]}>\n畫好後會傳給你(大約需要10分鐘)。'
                            message = TextSendMessage(text=message_text)
                            
                            
                            line_bot_api.reply_message(event.reply_token,message)
                        else:
                            line_bot_api.replay_message(event.reply_token,TextSendMessage(text=DefaultMessage))
                       
                        

                    elif event.message.type=='location':
                        
                        line_bot_api.replay_message(event.reply_token,TextSendMessage(text=DefaultMessage))

                    elif event.message.type=='video':
                        line_bot_api.replay_message(event.reply_token,TextSendMessage(text=DefaultMessage))


                    elif event.message.type=='sticker':
                        line_bot_api.replay_message(event.reply_token,TextSendMessage(text=DefaultMessage))

                    elif event.message.type=='audio':
                        line_bot_api.replay_message(event.reply_token,TextSendMessage(text=DefaultMessage))

                    elif event.message.type=='file':
                        line_bot_api.replay_message(event.reply_token,TextSendMessage(text=DefaultMessage))

                    elif isinstance(event, FollowEvent):
                        print('加入好友')
                        line_bot_api.replay_message(event.reply_token,TextSendMessage(text=DefaultMessage))

                    elif isinstance(event, UnfollowEvent):
                        print('取消好友')

                    elif isinstance(event, JoinEvent):
                        print('進入群組')
                        line_bot_api.replay_message(event.reply_token,TextSendMessage(text=DefaultMessage))

                    elif isinstance(event, LeaveEvent):
                        print('離開群組')
                        

                    elif isinstance(event, MemberJoinedEvent):
                        print('有人入群')
                        

                    elif isinstance(event, MemberLeftEvent):
                        print('有人退群')
                        

                    elif isinstance(event, PostbackEvent):
                        print('PostbackEvent')
#             print(PaintData)
            return HttpResponse()
        else:
            return HttpResponseBadRequest()
        


def data(request):
    
    with open('Upload/ImageGen.json','r+',encoding='UTF-8') as f:
        data = json.load(f)
        print(data)
        data1 = data.copy()
        data["read"]="Y"
        
        f.seek(0)  # rewind
        json.dump(data, f)
        f.truncate()      
    
    return JsonResponse(data1)

def images(request):
      
    try:
        image = request.GET["id"]
        image_path = f'Upload/{image}'
        with open(image_path, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        return HttpResponseBadRequest()
    
def resultImage(request):
      
    try:
        image = request.GET["id"]
        image_path = f'Result/{image}'
        print(image_path)
        with open(image_path, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        return HttpResponseBadRequest()
 
def resultVideo(request):
      
    try:
        video = request.GET["id"]
        video_path = f'Result/{video}'
        
        return stream_video(request, video_path)
    except IOError:
        return HttpResponseBadRequest()    
    
@csrf_exempt 
def uploadImage(request):
    
    if request.method == 'POST':
        
        imageFile = request.FILES['ImageFile']
        if imageFile :
            fs = FileSystemStorage()
            guid =uuid.uuid4().hex
            image_name = f"{guid}.png"
            fs.save(f"Result/{image_name}",imageFile)
            receiver = imageFile.name.split("_")[0]
            progress = int(imageFile.name.split("_")[1].split('.')[0])
            progress= progress/10
            
            print(f"Receiver:{receiver}")
            print(f"File uploaded:{image_name}")
            
            uploadToLINE(receiver,str(guid),"image",progress)
        return HttpResponse()
    else:
        return  HttpResponseBadRequest()

    
@csrf_exempt 
def uploadVideo(request):
    
    if request.method == 'POST':
        
        videoFile = request.FILES['VideoFile']
        imageFile = request.FILES['ImageFile']
        if videoFile :
            fs = FileSystemStorage()
            guid =uuid.uuid4().hex
            video_name = f"{guid}.mp4"
            image_name = f"{guid}.png"
            fs.save(f"Result/{video_name}",videoFile)
            receiver = videoFile.name.split(".")[0]
            
            fs.save(f"Result/{image_name}",imageFile)
            print(f"Receiver:{receiver}")
            print(f"File uploaded:{video_name}")
            
            uploadToLINE(receiver,str(guid),"video",100)
        return HttpResponse()
    else:
        return  HttpResponseBadRequest()

def uploadToLINE(receiver,fileName,mediaType,progress):
   
    
    sender = receiver
    if(mediaType=="image"):

#         上傳圖檔
        original_url= f"{settings.SITE_URL}resultImage?id={fileName}.png"
        preview_url= original_url
        print(f"URL:{original_url}")
        
        image_message = ImageSendMessage(
            original_content_url=original_url,
            preview_image_url=preview_url
            )
        txt_message=TextSendMessage(text=f"目前畫畫的進度{progress}%")
        line_bot_api.push_message(sender, txt_message)
        line_bot_api.push_message(sender, image_message)
        
    

#          上傳video
    if(mediaType=="video"):

        original_url= f"{settings.SITE_URL}resultVideo?id={fileName}.mp4"
        preview_url = f"{settings.SITE_URL}resultImage?id={fileName}.png"
        print(f"original_url:{original_url}")
        print(f"preview_url:{preview_url}")
        video_message = VideoSendMessage(
            original_content_url=original_url,
            preview_image_url=preview_url
        )

        image_message = ImageSendMessage(
                original_content_url=preview_url,
                preview_image_url=preview_url
                )
        txt_message=TextSendMessage(text="已經畫好囉!")


        line_bot_api.push_message(sender, txt_message)
        line_bot_api.push_message(sender, image_message)
        line_bot_api.push_message(sender, video_message)
        
    return
    
    
  

# streaming mp4 response

import os
import re
import mimetypes
from wsgiref.util import FileWrapper

from django.http.response import StreamingHttpResponse


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def stream_video(request, path):
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length), status=206, content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp
    
    
     
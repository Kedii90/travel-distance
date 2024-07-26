# coding: gbk
import pyaudio
import wave
import os
import pyttsx3
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import re


class Speak_assist:
    def __init__(self):
        # 初始化tts引擎
        self.engine = pyttsx3.init()
        # 设置发音人的性别和语音
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
    def run(self,text):
        # 将文本转换成语音
        self.engine.say(text)
        # 播放声音
        self.engine.runAndWait()
class Audio():
    def __init__(self):
        #self.filename = filename
        self.format = pyaudio.paInt16
        self.rate = 44100
        self.chunk = 1024
        self.duration = 5
        self.channels = 2
        self.audio_record = pyaudio.PyAudio()
        self.stream = self.audio_record.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.record = []
        #self.recording = True
        # self.wf = wave.open(self.filename, 'wb')
        # self.wf.setnchannels(self.channels)
        # self.wf.setsampwidth(self.audio_record.get_sample_size(self.format))
        # self.wf.setframerate(self.rate)

    def Start(self,filename,outfile):
        for i in range(0, int(self.rate / self.chunk * self.duration)):
            sound = self.stream.read(self.chunk)
            self.record.append(sound)
        self.filename = filename
        self.outfile = outfile
        self.wf = wave.open(filename, 'wb')
        self.wf.setnchannels(self.channels)
        self.wf.setsampwidth(self.audio_record.get_sample_size(self.format))
        self.wf.setframerate(self.rate)
        #self.recording = False
        self.Finish()

    def Finish(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio_record.terminate()
        self.wf.writeframes(b''.join(self.record))
        self.change()

    def change(self):
        # 利用pydub将wav格式转化为mp3格式
        # 格式不达标
        # audio = AudioSegment.from_file(self.filename,format='wav')
        # audio.export('output.mp3',format ='mp3')
        # 利用ffmpeg将wav格式转化为mp3格式
        cmd = r'E:\BigData\ffmpeg-2024-03-28-git-5d71f97e0e-essentials_build\bin\ffmpeg.exe -y -i ' + self.filename + ' -acodec  pcm_s16le -f s16le -ac 1 -ar 16000 '+ self.outfile
        os.system(cmd)
        #os.system('cls')

# 收到websocket消息的处理
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            #print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            print("请再说一遍：")

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # print(json.loads(message))
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            #print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
            txt=re.findall(r"'w': '(.*?)'",str(data),re.S)
            text.append(''.join(txt).strip('。'))


    except Exception as e:
        print("receive msg,but parse exception:", e)



# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws,a,b):
    print("### next ###")

text = []
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识
class Ws_Param(object):
    """
    利用科大讯飞web接口进行语音识别
    """
    # 初始化
    def __init__(self,filename):
        """
        科大讯飞申请获得如下信息，并填入如下信息
        """
        self.APPID = ''
        self.APIKey =''
        self.APISecret = ''
        self.filename = filename

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1,"vad_eos":10000}




    def create_url(self):
        """
        生成请求url
        :return: url
        """
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url




# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        frameSize = 8000  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧
        with open(wsParam.filename, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                # 发送第一帧音频，带business 参数
                # appid 必须带上，只需第一帧发送
                if status == STATUS_FIRST_FRAME:

                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())

def ws_start(filename):
    global wsParam
    wsParam = Ws_Param(filename=filename)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == '__main__':
    #录制音频
    recorder =Audio('output.wav',5)
    print("录音开始")
    recorder.Start()
    if not recorder.recording:
        print("录音结束")
        recorder.Finish()
        recorder.change()
    # wsParam = Ws_Param(APPID='e442b109', APISecret='NTI1NzU0YTE1NThmNmJkYjNkYmJjZGY3',
    #                    APIKey='6ac905bd6e6313303fdb5cd3bc73ac62',
    #                    AudioFile=r'output_change.pcm')
    # websocket.enableTrace(False)
    # wsUrl = wsParam.create_url()
    # ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    # ws.on_open = on_open
    # ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})




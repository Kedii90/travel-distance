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
        # ��ʼ��tts����
        self.engine = pyttsx3.init()
        # ���÷����˵��Ա������
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
    def run(self,text):
        # ���ı�ת��������
        self.engine.say(text)
        # ��������
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
        # ����pydub��wav��ʽת��Ϊmp3��ʽ
        # ��ʽ�����
        # audio = AudioSegment.from_file(self.filename,format='wav')
        # audio.export('output.mp3',format ='mp3')
        # ����ffmpeg��wav��ʽת��Ϊmp3��ʽ
        cmd = r'E:\BigData\ffmpeg-2024-03-28-git-5d71f97e0e-essentials_build\bin\ffmpeg.exe -y -i ' + self.filename + ' -acodec  pcm_s16le -f s16le -ac 1 -ar 16000 '+ self.outfile
        os.system(cmd)
        #os.system('cls')

# �յ�websocket��Ϣ�Ĵ���
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            #print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            print("����˵һ�飺")

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # print(json.loads(message))
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            #print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
            txt=re.findall(r"'w': '(.*?)'",str(data),re.S)
            text.append(''.join(txt).strip('��'))


    except Exception as e:
        print("receive msg,but parse exception:", e)



# �յ�websocket����Ĵ���
def on_error(ws, error):
    print("### error:", error)


# �յ�websocket�رյĴ���
def on_close(ws,a,b):
    print("### next ###")

text = []
STATUS_FIRST_FRAME = 0  # ��һ֡�ı�ʶ
STATUS_CONTINUE_FRAME = 1  # �м�֡��ʶ
STATUS_LAST_FRAME = 2  # ���һ֡�ı�ʶ
class Ws_Param(object):
    """
    ���ÿƴ�Ѷ��web�ӿڽ�������ʶ��
    """
    # ��ʼ��
    def __init__(self,filename):
        """
        �ƴ�Ѷ��������������Ϣ��������������Ϣ
        """
        self.APPID = ''
        self.APIKey =''
        self.APISecret = ''
        self.filename = filename

        # ��������(common)
        self.CommonArgs = {"app_id": self.APPID}
        # ҵ�����(business)��������Ի��������ڹ����鿴
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1,"vad_eos":10000}




    def create_url(self):
        """
        ��������url
        :return: url
        """
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # ����RFC1123��ʽ��ʱ���
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # ƴ���ַ���
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # ����hmac-sha256���м���
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # ������ļ�Ȩ�������Ϊ�ֵ�
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # ƴ�Ӽ�Ȩ����������url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # �˴���ӡ����������ʱ���url,�ο���demo��ʱ���ȡ���Ϸ���ӡ��ע�ͣ��ȶ���ͬ����ʱ���ɵ�url���Լ��������ɵ�url�Ƿ�һ��
        # print('websocket url :', url)
        return url




# �յ�websocket���ӽ����Ĵ���
def on_open(ws):
    def run(*args):
        frameSize = 8000  # ÿһ֡����Ƶ��С
        intervel = 0.04  # ������Ƶ���(��λ:s)
        status = STATUS_FIRST_FRAME  # ��Ƶ��״̬��Ϣ����ʶ��Ƶ�ǵ�һ֡�������м�֡�����һ֡
        with open(wsParam.filename, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                # �ļ�����
                if not buf:
                    status = STATUS_LAST_FRAME
                # ��һ֡����
                # ���͵�һ֡��Ƶ����business ����
                # appid ������ϣ�ֻ���һ֡����
                if status == STATUS_FIRST_FRAME:

                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # �м�֡����
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                # ���һ֡����
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # ģ����Ƶ�������
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
    #¼����Ƶ
    recorder =Audio('output.wav',5)
    print("¼����ʼ")
    recorder.Start()
    if not recorder.recording:
        print("¼������")
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




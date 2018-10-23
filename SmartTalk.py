# encoding:utf-8
import wave
from pyaudio import PyAudio, paInt16
import urllib2
import sys
import json
import time
import os

reload(sys)
sys.setdefaultencoding('utf-8')

#https://github.com/SpringZhang1978/SmartTalk.git
#本样例代码使用baidu在线语音识别、语音合成以及自然语音处理的功能，实现语音采集、录制、语音转文字、智能交互、文字转语音最好播放出来。
#本程序在python2.7以及win10环境下测试通过
#完成单轮聊天机器人功能。欢迎大家修改优化！

framerate=16000
NUM_SAMPLES=2000
channels=1
sampwidth=2
TIME=8
chunk = 2014

currentTime=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
#获取当前路径
pwd=os.getcwd()
def save_audio_file(filename,inputStream):
    '''save the data to the wavfile'''
    wf=wave.open(filename,'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(inputStream))
    wf.close()

#调用mic启动录制，以计时结束
#此处问题是如何能够智能识别对话结束
def start_record(secs):
    print("Start "+str(secs)+"s recording")
    pa=PyAudio()
    stream=pa.open(format = paInt16,channels=1,
                   rate=framerate,input=True,
                   frames_per_buffer=NUM_SAMPLES)
    inputaudio_buf=[]
    count=0
    while count<TIME*secs:#控制录音时间
        string_audio_data = stream.read(NUM_SAMPLES)
        inputaudio_buf.append(string_audio_data)
        count+=1
        print('.')
    recordAudioFileName = 'AudioRecord' + currentTime + '.wav'
    save_audio_file(recordAudioFileName,inputaudio_buf)
    stream.close()
    return recordAudioFileName

from aip import AipSpeech
APP_ID = '你的app_id'
API_KEY = '你的API_key'
SECRET_KEY = '你的 secret_key'

#以上app申请请移步baidu文档
#https://ai.baidu.com/docs#/Begin/top

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

#利用python sdk调用百度在线语音识别
def baidu_ASR(inputAudioFile):
    print("baidu_ASR"+inputAudioFile)
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    result = client.asr(get_file_content(inputAudioFile), 'wav', 16000, {
        'dev_pid': 1536,
    })
    resultWords = json.dumps(result['result'], ensure_ascii=False, encoding='utf-8')
    resultWordsStripped = resultWords[2:-2]
    print("baidu语音识别结果:" + resultWordsStripped)
    return resultWordsStripped
#获取baidu app access token，一个token可以使用2592000秒
def getUNITToken():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+API_KEY+'&client_secret='+SECRET_KEY
    request = urllib2.Request(host)
    request.add_header('Content-Type', 'application/json;charset=UTF-8')
    response = urllib2.urlopen(request)
    content = response.read()
    return json.loads(content).get("access_token")

#把baidu在线语音识别返回的文字传给baidu UNIT2.0做智能问答交互
def getSmartAnswer(inputText):
    inputText=inputText.encode(encoding='utf-8')
    url = 'https://aip.baidubce.com/rpc/2.0/unit/bot/chat?access_token={' + getUNITToken() + "}"
    bot_session = ''
    bot_id = '13450'
    post_data = {
        'log_id': '7758521',
        'version': '2.0',
        'request': {
            'user_id': '88888',
            'query_info': {
                'asr_candidates': [],
                'type': 'TEXT',
                'source': 'KEYBOARD'
            },
            'bernard_level': 1,
            'updates': '',
            'query': inputText,
            'client_session': '{"client_results":"", "candidate_options":[]}'
        },
        'bot_session': '',
        'bot_id': bot_id
    }

    print(json.dumps(post_data, ensure_ascii=False, encoding='utf-8'))
    request = urllib2.Request(url, json.dumps(post_data, ensure_ascii=False, encoding='utf-8'))
    request.add_header('Content-Type', 'application/Json_test;charset=UTF-8')
    response = urllib2.urlopen(request)
    resResult = response.read()
    print("Response:" + resResult)
    res2Json = json.loads(resResult)
    print '用户问: ' + inputText
    answer=res2Json['result']['response']['action_list'][0]['say']
    print 'baidu回答: ' + answer
    return answer

#调用baidu在线TTS功能把UNIT返回的文本回答转成mp3语音
def baiduTTS(inputText):
    aipClient= AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    ttsresult = aipClient.synthesis(inputText, 'zh', 2, {'vol': 5, 'per': 0})
    #per	String	发音人选择, 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
    answerAudioFileName='AudioAnswer'+currentTime+'.mp3'
    if not isinstance(ttsresult, dict):
        with open(answerAudioFileName, 'wb') as f:
            f.write(ttsresult)
    return answerAudioFileName
#播放wave音频
def playWave(audioFile):
    print("playAudio" + audioFile)
    wf=wave.open(audioFile,'rb')
    p=PyAudio()
    stream=p.open(format=p.get_format_from_width(wf.getsampwidth()),channels=
    wf.getnchannels(),rate=wf.getframerate(),output=True)
    while True:
        data=wf.readframes(chunk)
        if data=="":break
        stream.write(data)
    stream.close()
    p.terminate()

#直接调用系统播放器播放mp3
#此处疑问是寻找mp3库播放mp3文件，不需要打开系统播放器界面
def playMP3(audioFile):
    os.system(audioFile)


if __name__ == '__main__':
    print(pwd)
    audioRecordFile=start_record(5)
    audioASRResult=baidu_ASR(pwd+"\\"+audioRecordFile)
    answer = getSmartAnswer(audioASRResult)
    answerTTSAudioFile=baiduTTS(answer)
    playMP3(pwd+"\\"+answerTTSAudioFile)
    #playMP3("E:\\Robot\\Source\\baidu\\AudioRecord20181022175802.wav")

    print( 'Enjoy and submit your improvement!' )

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

framerate=16000
NUM_SAMPLES=2000
channels=1
sampwidth=2
TIME=8
chunk = 2014

currentTime=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
pwd=os.getcwd()
#recordAudioFileName='AudioRecord'+currentTime+'.wav'
#answerAudioFileName='AudioAnswer'+currentTime+'.wav'
def save_audio_file(filename,inputStream):
    '''save the data to the wavfile'''
    wf=wave.open(filename,'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(inputStream))
    wf.close()

def start_record(secs):
    print("Start "+str(secs)+"s recording")
    pa=PyAudio()
    stream=pa.open(format = paInt16,channels=1,
                   rate=framerate,input=True,
                   frames_per_buffer=NUM_SAMPLES)
    my_buf=[]
    count=0
    while count<TIME*secs:#控制录音时间
        string_audio_data = stream.read(NUM_SAMPLES)
        my_buf.append(string_audio_data)
        count+=1
        print('.')
    recordAudioFileName = 'AudioRecord' + currentTime + '.wav'
    save_audio_file(recordAudioFileName,my_buf)
    stream.close()
    return recordAudioFileName

from aip import AipSpeech
APP_ID = '14479635'
API_KEY = 'EsF6ng8HK8RHVTiAD21e4Gsl'
SECRET_KEY = 'n7jC2TyquYKTwQGwzDnIvKtCHQmeWUSq'

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

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

def getUNITToken():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=EsF6ng8HK8RHVTiAD21e4Gsl&client_secret=n7jC2TyquYKTwQGwzDnIvKtCHQmeWUSq'
    request = urllib2.Request(host)
    request.add_header('Content-Type', 'application/json;charset=UTF-8')
    response = urllib2.urlopen(request)
    content = response.read()
    return json.loads(content).get("access_token")

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

def baiduTTS(inputText):
    aipClient= AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    ttsresult = aipClient.synthesis(inputText, 'zh', 2, {'vol': 5, 'per': 0})
    #per	String	发音人选择, 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
    answerAudioFileName='AudioAnswer'+currentTime+'.mp3'
    if not isinstance(ttsresult, dict):
        with open(answerAudioFileName, 'wb') as f:
            f.write(ttsresult)
    return answerAudioFileName

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

def playMP3(audioFile):
    os.system(audioFile)


if __name__ == '__main__':
    print(pwd)
    audioRecordFile=start_record(6)
    audioASRResult=baidu_ASR(pwd+"\\"+audioRecordFile)
    answer = getSmartAnswer(audioASRResult)
    answerTTSAudioFile=baiduTTS(answer)
    playMP3(pwd+"\\"+answerTTSAudioFile)
    #playMP3("E:\\Robot\\Source\\baidu\\AudioRecord20181022175802.wav")

    print( 'Over!' )
from flask import Flask, render_template, jsonify

app = Flask(__name__)
from datetime import datetime, timezone, timedelta
import requests


from pymongo import MongoClient
import certifi
ca = certifi.where()
client = MongoClient('mongodb+srv://test:admin@cluster0.gctjvhr.mongodb.net/cluster0?retryWrites=true&w=majority', tlsCAFile = ca)
db = client.dbsparta


url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
service_key = "zC/WaF3+gxoHNz5XbzgfaPH/BqEta5PzQ04DtNdfoCZju8Sj00m3KGA04A58K5kzUU8Hu9gav1QtnKVYb5222A=="
KST = timezone(timedelta(hours=9))

year = datetime.now(KST).year
month = datetime.now(KST).month
day = datetime.now(KST).day
time = datetime.now(KST).hour
realmin = datetime.now(KST).minute
datetime=datetime.now(KST)
datetime=str(datetime)[0:10]
min = realmin
realdate = str(year) + str(month) + str(day)


print(datetime)

if realmin > 45 or realmin == 45 :
    min = '00'
else :
   time = time-1
   min = '30'

basetime = str(time) + str(min)
print(basetime)




# 웹 요청시 같이 전달될 데이터 = 요청 메시지
params = {
    'serviceKey': service_key,
    'numOfRows': 30,
    'pageNo': 1,
    'dataType': 'JSON',
    'base_date': realdate,  # 오늘 날짜
    'base_time': basetime,  # 요청 가능 발표 시간
    'nx': 60,  # 샘플 지역
    'ny': 127  # 샘플 지역
}


res = requests.get(url=url, params=params)
print(res.status_code, type(res.text), res.url)
items = res.json().get('response').get('body').get('items')


from pprint import pprint  # 구조있는 데이터를 더 편하게 보여줌

data = res.json()  # json.loads(res.text)와 같은 기능
datasort = data['response']['body']['items']['item'][6] , data['response']['body']['items']['item'][18],data['response']['body']['items']['item'][24]
pprint(datasort)
weather_data = dict()

for item in datasort:
    weather_data['Date'] = item['fcstDate']
    weather_data['basetime'] = basetime
    if item['category'] == 'T1H':
        weather_data['temp'] = item['fcstValue']

    if item['category'] == 'SKY':
        weather_data['sky_condition'] = item['fcstValue']

    if item['category'] == 'PTY':
        weather_data['rain'] = item['fcstValue']

    fcsttime = item['fcstTime'][0:2]
    if int(fcsttime) > 12 :
        fcsttime = int(fcsttime) -12
    weather_data['fcstTime'] = fcsttime


    if item['category'] == 'VEC':
        weather_data['wind_direction'] = item['fcstValue']
    if item['category'] == 'WSD':
        weather_data['wind_speed'] = item['fcstValue'][0:2]


pprint(weather_data)


@app.route('/')
def home():
    return render_template('index.html', datetime=datetime, sky_condition=weather_data['sky_condition'], rain=weather_data['rain'],temp=weather_data['temp'],basetime=weather_data['basetime'], fcstTime=weather_data['fcstTime'])



if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)


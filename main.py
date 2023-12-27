from flask import Flask, render_template, request, url_for
import requests
from datetime import datetime, timedelta
from decouple import config
import random


app = Flask(__name__)

api_key = config('API_KEY')

@app.route('/')
def index():
    return render_template('index.html', info_for_city=get_data_for_city('kyiv'))

def get_data_for_city(city):
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    response_api_url = requests.get(api_url)
    data = response_api_url.json()

    info = {}
    if response_api_url.status_code == 200:
        data_sunrise = datetime.utcfromtimestamp(data['sys']['sunrise']) + timedelta(hours=2)
        data_sunset = datetime.utcfromtimestamp(data['sys']['sunset']) + timedelta(hours=2)

        if data["weather"][0]["icon"][-1] == 'd':
            url_for_bg = random.choice(bg['day'])
        else:
            url_for_bg = random.choice(bg['night'])


        info = {
            'city_name' : data['name'],
            'temperature' : round(data['main']['temp'] - 273),
            'description' : data['weather'][0]['description'],
            'country' : data['sys']['country'],
            'feels_like' : round(data['main']['feels_like'] - 273),
            'speed_wind' : data['wind']['speed'],
            'sunrise' : data_sunrise.strftime('%H:%M'),
            'sunset' : data_sunset.strftime('%H:%M'),
            'humidity' : data['main']['humidity'],
            'pressure' : data['main']['pressure'],
            'visibility' : f"{data['visibility'] // 1000},{(data['visibility'] % 1000) // 100}",
            'src' : f'https://openweathermap.org/img/wn/{data["weather"][0]["icon"]}@2x.png',
            'url_for_bg' : url_for_bg,
        }

    return info


def get_info_all_day(city):
    api_urf_for_all_days = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}'
    response_all_days = requests.get(api_urf_for_all_days)
    data_all_days = response_all_days.json()

    if response_all_days.status_code == 200:
        info_all_days = data_all_days['list'][:8]

        for i in info_all_days:
            i['dt'] = datetime.utcfromtimestamp(i['dt']).strftime('%H:%M')
            i['main']['temp'] = round(i['main']['temp'] - 273)
            i['src_all_days'] = f"https://openweathermap.org/img/wn/{i['weather'][0]['icon']}@2x.png"

    info_all_days[0]['dt'] = 'now'
    return info_all_days

def get_info_few_days(city):
    api_urf_for_few_days = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}'
    response_few_days = requests.get(api_urf_for_few_days)
    data_few_days = response_few_days.json()

    info_few_days = [{}, {}, {}, {}, {}]
    
    if response_few_days.status_code == 200:

        few_days = data_few_days['list']
        today = datetime.now().date()

        current_dict, index_current_hour = 0, 0
        temp = []
        for i in few_days:
            date = datetime.strptime(i['dt_txt'], "%Y-%m-%d %H:%M:%S")
            day = date.date()
            if today != day:
                if date.hour == 12:
                    weather_icon = i['weather'][0]['icon'] 
                temp.append(i['main']['temp'])
                index_current_hour += 1
                if index_current_hour == 8 or few_days.index(i) == len(few_days)-1:
                    date_object = datetime.strptime(str(day), "%Y-%m-%d")
                    info_few_days[current_dict]['day_of_week'] = date_object.strftime("%a")
                    info_few_days[current_dict]['day'] = f'{date_object.day} {date_object.strftime("%B")}'
                    info_few_days[current_dict]['min_temp'] = round(min(temp) - 273)
                    info_few_days[current_dict]['max_temp'] = round(max(temp) - 273)
                    info_few_days[current_dict]['src'] = f"https://openweathermap.org/img/wn/{weather_icon}@2x.png"
                    current_dict += 1
                    temp = []
                    index_current_hour = 0

    return info_few_days


@app.route('/weather', methods=['POST', 'GET'])
def weather():
    if request.method == 'POST':
        city = request.form['city']
        try: 
            data_for_city = get_data_for_city(city)
            data_all_days = get_info_all_day(city)
            data_few_days = get_info_few_days(city)
        except Exception as e:
            return render_template('error.html')

        if data_for_city and data_all_days:
            return render_template('weather.html', info_for_city=data_for_city,
                                    info_all_days = data_all_days, few_days=data_few_days)
   
    return render_template('index.html')


bg = {
    'night' : ['https://mf-static.meteofor.st/assets/bg-desktop-wide/n_c1.jpg', 
               'https://media.istockphoto.com/id/514419350/uk/%D1%84%D0%BE%D1%82%D0%BE/%D0%BA%D1%80%D0%B0%D1%81%D0%B8%D0%B2%D1%96-%D0%B0%D0%B1%D1%81%D1%82%D1%80%D0%B0%D0%BA%D1%82%D0%BD%D1%96-%D0%BD%D1%96%D1%87%D0%BD%D1%96-%D1%85%D0%BC%D0%B0%D1%80%D0%B8.jpg?s=612x612&w=0&k=20&c=mzQ2u0_lY4Uyf6PLrl46sIs__9myW78bgL96nhc-zNw=',
               'https://media.istockphoto.com/id/915271866/uk/%D1%84%D0%BE%D1%82%D0%BE/%D0%BA%D0%B0%D1%80%D1%82%D0%B0-hdri-%D0%B7-%D0%B2%D0%B8%D1%81%D0%BE%D0%BA%D0%BE%D1%8E-%D1%80%D0%BE%D0%B7%D0%B4%D1%96%D0%BB%D1%8C%D0%BD%D0%BE%D1%8E-%D0%B7%D0%B4%D0%B0%D1%82%D0%BD%D1%96%D1%81%D1%82%D1%8E-%D0%BA%D0%B0%D1%80%D1%82%D0%B0-%D0%BD%D0%B0%D0%B2%D0%BA%D0%BE%D0%BB%D0%B8%D1%88%D0%BD%D1%8C%D0%BE%D0%B3%D0%BE-%D1%81%D0%B5%D1%80%D0%B5%D0%B4%D0%BE%D0%B2%D0%B8%D1%89%D0%B0-%D0%B4%D0%BB%D1%8F-%D0%BA%D1%96%D0%BD%D0%BD%D0%BE%D1%97-%D0%B5%D0%BA%D0%BA%D1%86%D1%96%D1%97-%D0%BD%D0%B0.jpg?s=612x612&w=0&k=20&c=yL6HF5LrdrITJfd50i6UQ-LcqwfD12nqkTLAZEQAh9k=',
               'https://media.istockphoto.com/id/450440297/uk/%D1%84%D0%BE%D1%82%D0%BE/%D0%BD%D1%96%D1%87%D0%BD%D0%B5-%D0%BD%D0%B5%D0%B1%D0%BE-%D0%B7-%D0%BC%D1%96%D1%81%D1%8F%D1%86%D0%B5%D0%BC-%D1%96-%D1%85%D0%BC%D0%B0%D1%80%D0%B0%D0%BC%D0%B8.jpg?s=612x612&w=0&k=20&c=DxoG4CH5grccBTN46A6onq6C40xZEp8CusRzh4nEm5w='
               ],
    'day' : ['https://media.istockphoto.com/id/823525718/uk/%D1%84%D0%BE%D1%82%D0%BE/%D1%8F%D1%81%D0%BA%D1%80%D0%B0%D0%B2%D0%B5-%D0%BD%D0%B5%D0%B1%D0%BE-%D1%96-%D1%81%D0%B2%D1%96%D0%B6%D0%B5-%D0%BF%D0%BE%D0%B2%D1%96%D1%82%D1%80%D1%8F-%D0%B4%D0%BB%D1%8F-%D1%84%D0%BE%D0%BD%D1%83.jpg?s=612x612&w=0&k=20&c=1fOiJrkj0QooMm3Zl1oqKM-H2OeLegS5sBqAFoisgH8=',
             'https://media.istockphoto.com/id/470918692/uk/%D1%84%D0%BE%D1%82%D0%BE/%D0%BA%D1%80%D0%B0%D1%81%D0%B8%D0%B2%D1%96-%D1%85%D0%BC%D0%B0%D1%80%D0%B8-%D0%BD%D0%B0-%D0%BD%D0%B5%D0%B1%D1%96.jpg?s=612x612&w=0&k=20&c=1vgaEQJyngYy0MMi8Y7NOAA2qMIm8gzC-3c5wEFwxJA=',
             'https://media.istockphoto.com/id/1203162244/uk/%D1%84%D0%BE%D1%82%D0%BE/%D0%BF%D0%B0%D0%BD%D0%BE%D1%80%D0%B0%D0%BC%D0%B0-%D0%BA%D1%80%D0%B0%D1%81%D0%B8%D0%B2%D0%BE%D0%B3%D0%BE-%D0%BF%D0%BE%D1%85%D0%BC%D1%83%D1%80%D0%BE%D0%B3%D0%BE-%D0%BD%D0%B5%D0%B1%D0%B0-%D0%BF%D1%80%D0%B8%D1%80%D0%BE%D0%B4%D0%B0-%D1%84%D0%BE%D0%BD%D1%83.jpg?s=612x612&w=0&k=20&c=FgInCMYFYYHEwFZwvABDwSnq3rYYSlPA-LEcgW4Hf-Y=',
    ]  
}
            
if __name__ == '__main__':
    app.run(debug=False, port=8080)

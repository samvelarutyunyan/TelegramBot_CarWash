import telebot
from telebot import types
import requests
import config
import json
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
import datetime

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start', 'hi', 'hello'])  # Считывает команду старт и выполняет функцию ниже
def main(message):
    bot.send_message(message.chat.id,
                     f"Привет, {message.from_user.first_name}!\nЯ Бот, который поможет тебе с мойкой твоей машины")


@bot.message_handler(commands=["geo"])
def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    button_back = types.KeyboardButton(text="Назад")
    keyboard.add(button_geo)
    keyboard.add(button_back)
    bot.send_message(message.chat.id, "Нажми на кнопку, чтобы передать мне свое местоположение", reply_markup=keyboard)
    telebot.types.ReplyKeyboardRemove()



@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "<b>Вот мои команды:</b>\n"
                                      "/start - запуск бота\n"
                                      "/settings - настройка бота\n"
                                      "/geo - отправить геопозицию боту\n"
                                      "/help - список команд", parse_mode='html')


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        print((message.location.latitude, message.location.longitude))
        lat = message.location.latitude
        lon = message.location.longitude
        res1 = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={config.API}&units=metric&lang=ru")
        data = json.loads(res1.text)
        temp = data["main"]["temp"]
        # description = data['weather'][0]['description']
        area = data['name']
        # icon = data["weather"][0]["icon"]
        feeling_temp = data["main"]["feels_like"]

        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.reverse(f"{lat}, {lon}", language='en')
        city = location.raw['address']['city']
        country = location.raw['address']['country']
        location_ru = geolocator.reverse(f"{lat}, {lon}", language='ru')
        city_ru = location_ru.raw['address']['city']
        country_ru = location_ru.raw['address']['country']

        url2 = f"https://meteoinfo.ru/forecasts/{str.lower(country)}/{str.lower(city)}-area/{str.lower(city)}"
        r = requests.get(url2)
        soup = BeautifulSoup(r.text, 'html.parser')
        mas = []
        quotes = soup.find_all('td', class_='td_short_gr')
        for quote in quotes:
            mas.append(quote.text)
        print(mas)


        #Разделение на день и ночь
        den = []
        noch = []
        for i in range(5):
            den.append(mas[i + 25])
            noch.append(mas[i + 66])


        # Проверка на осадки и вывод эмодзи
        emoji = []
        for i in range(5):
            if ("снег" in den[i]) or ("снег" in noch[i]) or ('метель' in den[i]) or ('метель' in noch[i]) or (
                    'дождь' in den[i]) or ('ливень' in den[i]) or ('дожди' in den[i]) or ('ливни' in den[i]) or (
                    'кратковременный дождь' in den[i]) or ('кратковременные осадки' in den[i]) or (
                    'дождь' in noch[i]) or (
                    'ливень' in noch[i]) or ('дожди' in noch[i]) or ('ливни' in noch[i]) or (
                    'кратковременный дождь' in noch[i]) or ('кратковременные осадки' in noch[i]):
                emoji.append("🌧")
            else:
                emoji.append("☀️")


        # Вывод текста в сообщении месяц, день и т.д
        current_date = datetime.datetime.now()
        today = datetime.date.today()
        weekday = today.weekday()
        days = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Cуббота", 6: "Воскресенье"}
        months = ['', 'Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября',
                  'Ноября', 'Декабря']

        bot.send_message(message.chat.id, f'{country_ru}, {city_ru}, Район {area}\n\n{days[weekday]}, {current_date.day} {months[current_date.month]} {emoji[0]}\n\nДень: {round(float(temp))}°C\nОщущается как: {round(float(feeling_temp))}°C\n{mas[25]}\n'
                                          f'\nНочь: {mas[58]}C\n{mas[66]}')
        weekday+=1
        for i in range(1,5):
            bot.send_message(message.chat.id, f'\t{days[weekday]}, {current_date.day + i} {months[current_date.month]} {emoji[i]}\n\nДень {mas[i+17]}C\n{mas[i+25]} \n\nНочь {mas[i+58]}C\n{mas[i+66]}')
            weekday+=1
            if weekday == 7:
                weekday = 0


        # Определение нужно ли вывести автомойки или нет
        if '🌧' in emoji[:1]:
            bot.send_message(message.chat.id, "Ожидаются дожди 🌧\nМашину лучше не мыть в ближайшее время.\nВозьми с собой зонт. ☔ ️")

        else:
            text = f"[Ближайшие автомойки](https://yandex.ru/maps/213/{city}/category/car_wash/184105244/?ll={lon}%2C{lat}&sll={lon}%2C{lat}&z=10)"
            bot.send_message(message.chat.id, "Дожди за эту неделю не ожидаются! ☀️")
            bot.send_message(message.chat.id, f"{text}", parse_mode='MarkdownV2')


# @bot.message_handler(commands=['settings'])
# def settings(message):
#     print(123)


@bot.message_handler()
def info(message):
    if message.text.lower() == 'назад':
        bot.send_message(message.chat.id, f"Вы вернулись в меню", reply_markup=None)


bot.polling(none_stop=True)

import requests
import os
import re
import json
from out_acts import choose_act


def check_dir(directory):
    if not os.path.exists(directory):
        return 0
    return 1

def delete_file(filename:str,directory='.'):
    try:
        path = os.path.join(directory,filename)
        os.remove(path)
        return 1
    except Exception as e:
        return e

def saved_directory(act:str,directory=''):
    if act == 'w' and directory:
        if check_file_exists('chart_bot.json',r'C:\bot_config'):
            os.remove(os.path.join(r'C:\bot_config','chart_bot.json'))
        with open(r'C:\bot_config\chart_bot.json','w') as f:
            data = {'save_directory':directory}
            json.dump(data,f)
        return True
    elif act == 'r':
        if check_file_exists('chart_bot.json',r'C:\bot_config'):
            with open(r'C:\bot_config\chart_bot.json','r') as f:
                data = json.load(f)
            return data['save_directory']
        return False
    return False

def input_icao():
    while True:
        airport = input('Введите ICAO аэропорта: ')
        if not re.fullmatch('[A-z]{4}', airport):
            print('Неправильный формат ICAO')
        else:
            return airport
        print('Если вы хотите отменить действие нажмите Enter вместо ввода ICAO')
        if not airport:
            return False

def input_directory():
    while True:
        directory = input('Введите директорию для сохранения чартов, нажмите Enter чтобы сохранить в текущую директорию или введите 1 чтобы сохранить в директорию по умолчанию\n - ')
        if directory == '1':
            a = saved_directory('r')
            if a:
                return a
            print('Сохраненной директории не найдено, введите ее заново')
        elif not directory:
            return 1
        else:
            if check_dir(directory):
                print('Хотите ли вы сохранить эту директорию для будущего использования\n1 - да\n2 или любой другой символ - нет')
                a = input(' - ')
                if a == '1':
                    saved_directory('w',directory)
                    print('Директория сохранена')
                return directory
            else:
                print('Такой директори нет')
                a = input('Напишите 1 если хотите отменить действие: ')
                if a == '1':
                    return False

def check_file_exists(filename, directory):
    file_path = os.path.join(directory, filename)
    return os.path.exists(file_path)

def chart(port:str,directory="."):
    airport = port.upper()
    if check_file_exists(f'{airport}.pdf',directory):
        return 'чарты уже скачаны',1
    try:
        url = f'https://lukeairtool.net/viewchart.php?icao={airport}'
        file = requests.get(url)
        with open(os.path.join(directory,f'{airport}.pdf'),'wb') as f:
            f.write(file.content)
        return 'чарты успешно скачаны',0
    except Exception as e:
        return 'ошибка',e


def charts_main():
    acts = ['загрузить чарты', 'обновить чарты', 'выйти из загрузчика']
    choice = choose_act(acts)
    if not choice:
        return True
    elif choice == '3':
        return False
    elif choice == '1':
        airport = input_icao()
        if not airport:
            return True
        data = [airport]
        a = input_directory()
        if not a:
            return False
        if a != 1:
            data.append(a)
        result = chart(*data)
        if result[0] == 'ошибка':
            print('Возникла ошибка:\n' + result[1])
        else:
            print(result[0])
    elif choice == '2':
        airport = input_icao()
        if not airport:
            return True
        data = [f'{airport.upper()}.pdf']
        a = input_directory()
        if not a:
            return True
        if a != 1:
            data.append(a)
        dels = delete_file(*data)
        if dels != 1:
            print(dels)
            return True
        data[0] = airport

        result = chart(*data)
        if result[0] == 'ошибка':
            print('Возникла ошибка:\n' + result[1])
        else:
            print(result[0])
        return True


print('Благодарю за использование данного загрузчика')


def choose_act(acts:list):
    print('Выберите действие:')
    for num, act in enumerate(acts,1):
        print(f'{num} - {act}')
    choice = input(f'Выберите вариант 1-{len(acts)}: ')
    if choice not in [str(i) for i in range(1,len(acts)+1)]:
        print('Такого варианта нет')
        return False
    return choice
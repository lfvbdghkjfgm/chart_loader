from charts import charts_main
from out_acts import choose_act



def main():
    while True:
        acts = ['загрузить чарты', 'выйти из приложения']
        choice = choose_act(acts)
        if not choice:
            continue
        if choice == '1':
            act = charts_main()
            if not act:
                break
        elif choice == '3':
            break




if __name__ == '__main__':
    main()



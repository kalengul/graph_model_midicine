# Печать списков в столбец
def print_list(list, label = None):
    if label:
        print(f'{label}:')

    # Если список пуст
    if not list or list == []:
        print('\tСписок пуст\n')
        return
    else:
        for item in list:
            print(f'\t{item}')
    print()
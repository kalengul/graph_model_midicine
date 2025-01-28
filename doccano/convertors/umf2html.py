
test_umf = [('средства, действующие на ренин-ангиотензиновую систему', 'group'), (';', None), ('ингибиторы ангиотензинпревращающего фермента (АПФ)', 'group'), (', комбинации;', None), ('ингибиторы АПФ и блокаторы кальциевых каналов', 'group'), ('.', None), ('Фармакодинамика', None), ('Амлодипин', 'prepare'), ('Механизм действия', None), ('Амлодипин', 'prepare'), ('-', None), ('БМКК, производное дигидропиридина', 'group'), ('.', None), ('Антигипертензивное действие', 'mechanism'), ('амлодипина', 'prepare'), ('обусловлено', None), ('прямым расслабляющим воздействием', 'mechanism'), ('на', 'prepare'), ('гладкомышечные клетки сосудистой стенки', 'mechanism'), ('.', None)]

def umf2html(data):
    # Начало
    html_content = '<div class="entities" style="line-height: 2.5; direction: ltr">\n'

    for text, tag in data:
        # При наличии тега
        if tag:
            html_content += (
                    f'<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; '
                    f'margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">\n'
                        f'\t{text} '
                        f'\n\t<span style="font-size: 0.8em; font-weight: bold; line-height: 1; '
                        f'border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem;">'
                        f'{tag}'
                        f'</span>\n'
                    f'</mark>\n'
                )
        # При отсутсвии тега
        else:
            html_content += f'\t{text}\n'

    # Конец документа
    html_content += '</div>'

    return html_content

if __name__ == "__main__":
    with open(f"convertors\\test\\test_umf2html.svg", 'w', encoding='utf-8') as f:
        f.write(umf2html(test_umf))
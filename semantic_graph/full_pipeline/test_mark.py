import tkinter as tk
from tkinter import messagebox
import re

# Создаем главное окно
root = tk.Tk()
root.title("Текстовая аннотация")

# Создаем текстовое поле для отображения и редактирования текста
text_widget = tk.Text(root, wrap="word", font=("Arial", 14))
text_widget.pack(expand=True, fill="both")

# Пример текста
sample_text = "Это пример текста для аннотации. Выберите слово для пометки."
text_widget.insert(tk.END, sample_text)

# Заранее определенные теги и их цвета
TAGS = {
    "Подлежащее": "lightblue",
    "Сказуемое": "lightgreen",
    "Дополнение": "lightyellow",
    "Определение": "lightcoral"
}

# Переменная для выбранного тега
selected_tag = tk.StringVar(value="Подлежащее")  # Тег по умолчанию

def apply_tag(event):
    try:
        # Получаем текущий выбранный тег
        tag = selected_tag.get()

        # Получаем начальную и конечную позицию выделения
        start = text_widget.index(tk.SEL_FIRST)
        end = text_widget.index(tk.SEL_LAST)

        # Определяем границы выделенного диапазона
        start_line, start_col = map(int, start.split("."))
        end_line, end_col = map(int, end.split("."))

        # Применяем выбранный тег ко всем словам в выделенной области
        text_widget.tag_configure(tag, background=TAGS[tag], foreground="black")

        for line in range(start_line, end_line + 1):
            line_start = f"{line}.0"
            line_end = f"{line}.end"
            
            if line == start_line:
                line_start = start
            if line == end_line:
                line_end = end

            text = text_widget.get(line_start, line_end)
            for match in re.finditer(r'\S+', text):
                word_start = text_widget.index(f"{line_start} + {match.start()}c")
                word_end = text_widget.index(f"{line_start} + {match.end()}c")
                if not any(text_widget.tag_ranges(tag) and text_widget.tag_nextrange(tag, word_start, word_end)):
                    text_widget.tag_add(tag, word_start, word_end)

    except tk.TclError:
        # Ничего не делаем, если нет выделения
        pass

def select_word(event):
    text_widget = event.widget
    index = text_widget.index(f"@{event.x},{event.y}")
    start, end = get_word_bounds(text_widget, index)

    # Пропустить пробелы и знаки препинания в начале и конце слова
    while start > "1.0" and text_widget.get(start + "-1c") in " ,.":
        start = text_widget.index(f"{start} - 1c")

    while end < tk.END and text_widget.get(end) in " ,.":
        end = text_widget.index(f"{end} + 1c")

    # Очищаем текущее выделение и выделяем слово целиком
    text_widget.tag_remove(tk.SEL, "1.0", tk.END)
    text_widget.tag_add(tk.SEL, start, end)
    text_widget.mark_set(tk.INSERT, end)
    text_widget.see(tk.INSERT)

    # Настраиваем стиль выделения
    text_widget.tag_config(tk.SEL, background=text_widget.cget('background'), foreground=text_widget.cget('foreground'))

def set_tag(tag):
    selected_tag.set(tag)
    messagebox.showinfo("Тег выбран", f"Выбран тег: '{tag}'")

def get_word_bounds(text_widget, index):
    """Возвращает границы слова, в котором находится индекс."""
    start = text_widget.index(f"{index} wordstart")
    end = text_widget.index(f"{index} wordend")
    return start, end

# Добавляем кнопки для каждого тега
button_frame = tk.Frame(root)
button_frame.pack(side="bottom", pady=10)

for tag, color in TAGS.items():
    button = tk.Button(button_frame, text=tag, bg=color, command=lambda t=tag: set_tag(t))
    button.pack(side="left", padx=5)

# Привязываем события
text_widget.bind("<Button-1>", select_word)
text_widget.bind("<ButtonRelease-1>", apply_tag)

# Запуск главного цикла приложения
root.mainloop()

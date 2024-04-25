import nltk
import string
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.probability import FreqDist
from nltk import word_tokenize
nltk.download('punkt')
import pymorphy2
import re


'''
Данных модуль реализует предобработку текстов.
Предоставляются как инструменты для первичной предобработки, так и инструменты
для токенизации, лемматизации, удаления стоп-слов, очистка от цифр, латинских букв, 
получения частотного словаря.
'''

# класс Строитель для первичной предобработки текста
class TextBuilder:
    def __init__(self, text: str) -> None:
        self.text = text
    
    # перевод текста в нижний регист
    def set_lower(self) -> None:
        self.text = self.text.lower()
        return self

    # замена ё на е
    def replace_yo(self) -> None:
        self.text = self.text.replace('ё', 'е')
        return self

    # удаление знаков парепинания
    def removing_punctuation(self, spec_chars:str = None, replaced = False) -> None:
        '''
        spec_chars - набор символов для фильтрации. 
        Если replaced - False, добавляется к уже заданным внутри символам,
        если True, то замещает полностию внутренний набор символов.
        ''' 
        punctuation = string.punctuation + '\n\xa0«»\t—…‘’‚›®°“”‹¢£¥€©§„№é™'
        if spec_chars and replaced:
            punctuation = spec_chars
        elif spec_chars:
            punctuation += spec_chars
        self.text = ''.join([ch for ch in self.text if ch not in punctuation])
        return self
    
    #cпециальный метод для возвращения результата работы методов класс TextBuilder предварительной обработки текстов.
    def get_result(self) -> str:
        return self.text

# метод токенизации 
def tokenization(text: str) -> list[str]:
    '''
    По факту разбивает принимает на вход предложение или несколько предложений
    в виде строки, разбивает эту строку на слова,
    и возравает список слов в виде списка строк.
    '''
    return word_tokenize(text)

# метод удаления последоватьности только цифр
def removing_digits(word_tokens: list[str]) -> list[str]:
    return [re.sub('\d+', '', word_token) for word_token in word_tokens if not word_token.isdigit()]

# метод удаления последоватьности символов, содержацих цифры
def removing_digits_absolute(word_tokens: list[str]) -> list[str]:
    return [word_token for word_token in word_tokens if word_token.isalpha()]

# 
def removing_latin_literals(word_tokens: list[str]) -> list[str]:
    return [word_token for word_token in word_tokens if not bool(re.search('[a-z]', word_token))]

# метод удаления латинских цифр
def removing_SW(text: list[str], external_stop_words: list[str] = None) -> list[str]:
    stop_words = stopwords.words("russian")
    if external_stop_words:
        stop_words = external_stop_words
    return [word for word in text if word not in stop_words]

# метод лематизации - приведение слов в нормальную форму
def lemmatization(word_tokens: list[str]) -> list[str]:
    morph = pymorphy2.MorphAnalyzer()
    lemm_word_tokens = [morph.parse(word_token)[0].normal_form for word_token in word_tokens]
    return lemm_word_tokens

# метод для построения частотного словаря
def frequency_dictionary(text_tokens: list[str]) -> dict[str, int]: 
    '''
    Входные данные - список слов (строк).
    Выходные данные - словарь, ключами которого являются слова (строки), 
    значениями частоты их появления во входном списке слов (целые числа).
    '''
    text = nltk.Text(text_tokens)
    return FreqDist(text)


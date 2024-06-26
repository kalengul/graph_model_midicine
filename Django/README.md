# Web-site on Django

Архитектура. Фреймворк Django ввел новую терминологию MTV. 
В Django функции, отвечающие за обработку логики, соответствуют части Controller из MVC, но называются View, а отображение соответствует части View из MVC, но называется Template. Получилось, что:

M -> M Модели остались неизменными
V -> T Представление назвали Templates
C -> V Контроллеры назвали Views

Вся логика при таком подходе вынесена во View, а то, как будут отображаться данные в Template. Из-за ограничений HTTP протокола, View в Django описывает, какие данные будут представленны по запросу на определенный URL. View, как и протокол HTTP, не хранит состояний и по факту является обычной функцией обратного вызова, которая запускается вновь при каждом запросе по URL. Шаблоны (Templates), в свою очередь, описывают, как данные представить пользователю.

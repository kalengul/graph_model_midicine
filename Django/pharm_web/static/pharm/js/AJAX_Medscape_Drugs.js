
    // Получаем поле поиска и добавляем обработчик события ввода
    var searchInput = document.getElementById('search-input-medicines');
    searchInput.addEventListener('input', function() {
        // Получаем значение поля
        var query = searchInput.value;
        // Отправляем AJAX запрос на URL "/search/" с параметром "q" равным значению поля
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/search/?q=' + query);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.send();
        // Обрабатываем полученный ответ
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Получаем список препаратов из ответа
                var drugs = JSON.parse(xhr.responseText).drugs;
                // Очищаем предыдущие подсказки
                var suggestions = document.getElementById('suggestions');
                suggestions.innerHTML = '';
                // Добавляем новые подсказки в список
                for (var i = 0; i < drugs.length; i++) {
                    var drug = drugs[i];
                    var suggestion = document.createElement('li');
                    // Добавляем значение и id препарата в элемент списка
                    suggestion.textContent = drug.name;
                    suggestion.dataset.id = drug.id;
                    suggestions.appendChild(suggestion);
                }
            }
        }
    });

function selectDrug(event) {
    // Получаем выбранный элемент списка
    var selected = event.target;
    // Получаем значение и id препарата
    var name = selected.textContent;
    var id = selected.dataset.id;
    // Добавляем значение и id в поле поиска
    let text = searchInput.value;
    console.log(text);
    words = text.split(", ");
    console.log(words);
    text=words.slice(0, -1).join(', ');
    console.log(text);
    if (text!='') { text=text+', '}
    searchInput.value = text;
    searchInput.value += name + ', ';
    searchInput.dataset.id += id + ', ';
    // Удаляем часть строки, по которой осуществлялся поиск
  var part = searchInput.dataset.part;
  console.log(part);
  // Ищем первое вхождение подстроки в строку
  var index = searchInput.value.indexOf(part);
  if (index >= 0) {
    // Если подстрока найдена, удаляем ее из строки
    searchInput.value = searchInput.value.substring(0, index) + searchInput.value.substring(index + part.length);
    // Сбрасываем значение части строки
    searchInput.dataset.part = '';
  }
    // Очищаем список подсказок
    var suggestions = document.getElementById('suggestions');
    suggestions.innerHTML = '';
}

var suggestions = document.getElementById('suggestions');
suggestions.addEventListener('click', selectDrug);



const xlsx = require('xlsx')

console.log("Парсинг ЛС и Побочек")

const file = xlsx.readFile('./Data/SideEffectTable.xlsx')

let data = []

const sheets = file.SheetNames //получение Массива с именами страниц
console.log(sheets)

//Считываем данные из страницы 'Пересчет ранг на %'
const temp = xlsx.utils.sheet_to_json(
    file.Sheets[file.SheetNames[sheets.length-1]])
    temp.forEach((res) => {
        data.push(res)
    }
)

//Преобразование данных в нужный формат
let newData = []
data.forEach(string => { //Проходим по всем строкам
    if("DRAG" in string){ //Есле в строке есть данные по ключу DRAG
        Object.keys(string).forEach(key => {
            //console.log(`Ключ: ${key}, Значение: ${string[key]}`);
            if (key!="DRAG"){
                let newString = {}
                newString.DRAG = string.DRAG
                newString.SideEffect = key
                newString.P = string[key]

                //console.log(newString)
                newData.push(newString);
            }
            
        });
    }
})

//Запись преобразованных данных в новый лист
const ws = xlsx.utils.json_to_sheet(newData)
xlsx.utils.book_append_sheet(file,ws,"ParseData")
xlsx.writeFile(file,'./Data/SideEffectTable.xlsx')


//Записб в txt файл
const fs = require('fs');

fs.writeFile('./Data/data.txt', JSON.stringify(data, null, 2), (err) => {
  if (err) throw err;
  console.log('Данные успешно записаны в data.json');
});

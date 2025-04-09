import express from 'express';
import cors from 'cors'
import fileUpload from 'express-fileupload';
import fs from "fs"
import path from "path";
import { fileURLToPath } from "url";

import router from "./api/routes.mjs"

const app = express();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

//Конвейер обраотки запросов
app.use(cors({
    credentials: true,
    origin: ["http://localhost:5173"],
    optionsSuccessStatus: 200
  },
  {
    credentials: true,
    origin: ["http://0.0.0.0:5173"],
    optionsSuccessStatus: 200
  },
)
);
app.use(express.json({ extended: true }))
app.use(express.static(path.resolve(__dirname,'statis/files/json'))) //Доступ к статическим файлам c графами
app.use(express.static('public'))
app.use(fileUpload({}))
app.use('/', router);

//app.use('/', (req, res) => res.status(200).send('HEALTHY'));

const { SERVER_PORT: port = 7000 } = process.env;
//Старт сервера
const startApp = async()=>{
    try {
        app.listen({ port }, () => {
            console.log(`Server ready at http://0.0.0.0:${port}`);
        });
    } catch (error) {
        console.log(error)
    }
}

startApp()





















// import {GraphParser} from "./modules/GraphParser/GraphParser.mjs"
// import {TemplateHandlers} from "./modules/TemplateHandlers.mjs"
// import {XlsxManeger} from "./modules/XlsxManeger.mjs"

// import fs from "fs"
// import path from "path";
// import { fileURLToPath } from "url";

// //Создание html отображения графа
// const CreateHTML = (graphJSON, htmlFileName) =>{
//     //Парсинг графа
//     const window = {width: 1200, height:  600, xStep:50, yStep: 100}
//     const nodeView = { r: 30 }
//     const  graphParser = new GraphParser();

//     graphParser.Parse(graphJSON, window, nodeView)


//     //Формирование выходного файла
//     const fileName = `${htmlFileName}.html`

//     const __filename = fileURLToPath(import.meta.url);
//     const __dirname = path.dirname(__filename);
//     const outputPath = path.join(__dirname, "GraphsExcel", "models" , fileName);

//     //Формирование html из шаблона
//     const templateHandlers = new TemplateHandlers()
//     templateHandlers.compileTemplate("graph.hbs", {
//         graphName: graphJSON.name,
//         graphData: JSON.stringify(graphJSON),
//         window: JSON.stringify(window),
//     }).then(data =>{
//         //Запись html в файл
//         fs.writeFileSync(outputPath, data);
//     })

//     return `./models/${fileName}`
// }


// const ReadFolder = () =>{
//     const __filename = fileURLToPath(import.meta.url);
//     const __dirname = path.dirname(__filename);
    
//     // Путь к папке с JSON-файлами
//     const folderPath = path.join(__dirname, 'drug_json_graphs');

//     // Чтение всех файлов из папки
//     fs.readdir(folderPath, (err, files) => {
//         if (err) {
//             console.error('Ошибка при чтении папки:', err);
//             return;
//         }
    
//         // Фильтрация только JSON-файлов
//         const jsonFiles = files.filter(file => path.extname(file).toLowerCase() === '.json');
    
//         if (jsonFiles.length === 0) {
//             console.log('JSON-файлы не найдены.');
//             return;
//         }
    
//         console.log(`Найдено ${jsonFiles.length} JSON-файлов:`);
    
//         // Обработка каждого JSON-файла
//         jsonFiles.forEach(file => {
//         const filePath = path.join(folderPath, file);
    
//             // Чтение содержимого файла
//             fs.readFile(filePath, 'utf8', (err, data) => {
//                 if (err) {
//                     console.error(`Ошибка при чтении файла ${file}:`, err);
//                     return;
//                 }
        
//                 try {
//                     // Парсинг JSON
//                     const graphCopy = JSON.parse(data);

//                     let htmlFileName = file.slice(0, - path.extname(file).length)

//                     //Формирование html
//                     const htmlPath = CreateHTML(graphCopy, htmlFileName);
//                     const drugId = graphCopy.name

//                     //Запись гиперссылки в файл
//                     const fileXlsx = path.join(__dirname, "GraphsExcel", "ProcessOfInstructionsMarking.xlsx");

//                     const xlsxManeger = new XlsxManeger(fileXlsx);
//                     xlsxManeger.AddHiperLink(htmlPath, drugId, 'Графы')

                            
//                 } catch (parseError) {
//                     console.error(`Ошибка при парсинге JSON в файле ${file}:`, parseError);
//                 }
//             });
//         });
//     });
// }

// ReadFolder();

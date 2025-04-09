import fs from "fs"
import path from "path";
import archiver from 'archiver';
import fsExtra from 'fs-extra'
import { fileURLToPath } from "url";
import { v4 as uuid } from 'uuid';
import os from 'os';
import xlsx from "xlsx"

import db from '../../db/db.mjs';
import { SqlRequests } from "../../db/sqlRequests.mjs";

const sqlRequests = new SqlRequests()

import {GraphParser} from "../../modules/GraphParser/GraphParser.mjs"
import {TemplateHandlers} from "../../modules/TemplateHandlers.mjs"
import { error } from "console";

//Создание html отображения графа
const CreateHTML = (graphJSON, outputPath) =>{
    console.log('Формирование html')
    console.log(outputPath)
    //console.log(graphJSON)
    //Парсинг графа
    const window = {width: 1200, height:  600, xStep:50, yStep: 100}
    const nodeView = { r: 30 }
    const  graphParser = new GraphParser();

    const resultParse = graphParser.Parse(graphJSON, window, nodeView)
    console.log(resultParse)

    //Формирование html из шаблона
    const templateHandlers = new TemplateHandlers()
    templateHandlers.compileTemplate("graph.hbs", {
        graphName: graphJSON.name,
        graphData: JSON.stringify(graphJSON),
        window: JSON.stringify(window),
    }).then(data =>{
        //Запись html в файл
        
        fs.writeFileSync(outputPath, data);
    }).catch(err=>{
        console.error('Ошибка формирования шаблона')
        console.error(err)
    })
}

// Функция добавления файлов в архив (рекурсивная)
async function addFilesToArchive(archive, sourceDir, relativePath) {
    try {
        const files = await fsExtra.readdir(sourceDir);
        for (const file of files) {
            const filePath = path.join(sourceDir, file);
            const stat = await fsExtra.stat(filePath);
            if (stat.isDirectory()) {
                await addFilesToArchive(archive, filePath, path.join(relativePath, file));
            } else {
                archive.file(filePath, { name: path.join(relativePath, file) });
            }
        }
    } catch (error) {
        console.error(`Ошибка при добавлении файлов из ${sourceDir}:`, error);
        throw error;
    }
}

// Функция для удаления временной директории
async function cleanup(tempDir) {
    if (tempDir) {
        try {
            await fsExtra.remove(tempDir);
            console.log(`Временная директория ${tempDir} удалена`);
        } catch (removeError) {
            console.error('Ошибка при удалении временной директории:', removeError);
        }
    }
}

export class MarkForInstructions {
    async AddNewDrug(req,res){
        const {file, drug_name} = req.body

        if(!drug_name) return res.status(400).json({message:"Не указано название нового лекарственного средства"})

        let status;
        if(req.body.status) status = req.body.status;
        else status = null

        const __filename = fileURLToPath(import.meta.url);
        const __dirname = path.dirname(__filename);

        if(req.files){ //Если пришел файл со схемой
            let fileName_json = uuid() + '.json';
            let filePath_json = path.resolve(__dirname, '..', '..','static','files', 'json', fileName_json)

            //Получение файла из исходголо заголовка
            let uploadedFile = req.files.file;
            let titleFile = uploadedFile.name
            console.log(titleFile)

            let titleArr =  titleFile.split(".")
            let graph_name =titleArr[0]; //Сохранение имени файла без расширения

            // Перемещаем файл json
            await new Promise((resolve, reject) => {
                uploadedFile.mv(filePath_json, function(err) {
                    if (err) reject(err);
                    else resolve();
                });
            });

            let fileName_html = uuid() + '.html';
            let filePath_html = path.resolve(__dirname,'..', '..','static','files', 'html', fileName_html)

            //Читаем файл и формируем html
            await fs.readFile(filePath_json, 'utf8', (err, data) => {
                if (err) {
                    console.error(`Ошибка при чтении файла ${file}:`, err);
                    return;
                }
                try {
                    // Парсинг JSON
                    const graphCopy = JSON.parse(data);

                    //console.log(data)

                    //Формирование html
                    CreateHTML(graphCopy, filePath_html);
                            
                } catch (parseError) {
                    console.error(`Ошибка при парсинге JSON в файле ${file}:`, parseError);
                }
            });

            //Запись данных в файл
            const drugName = drug_name.toUpperCase();
            db.run(sqlRequests.AddNewDrug(), [drugName, status, graph_name, fileName_json, fileName_html], function (err) {
                if (err || this.changes === 0) {
                    console.error(err);
                    return res.status(400).json({ message: 'Ошибка при добавлении лекарственного сребсва' });
                }
                return res.status(200).json({ message: `Лекарственное срадство ${drug_name} добавлено` });
            });
        }
        else{
            //Запись данных в файл
            const drugName = drug_name.charAt(0).toUpperCase() + drug_name.slice(1).toLowerCase()


            db.run(sqlRequests.AddNewDrug(), [drugName, status, null, null, null], function (err) {
                if (err || this.changes === 0) {
                    console.error(err);
                    return res.status(400).json({ message: 'Ошибка при добавлении лекарственного сребсва' });
                }
                return res.status(200).json({ message: `Лекарственное срадство ${drug_name} добавлено` });
            });
        }
            
    }

    async GetGraphStatus(req, res){
        const statuses = [
            "Завершен",
            "В процессе",
            "Недостаточно информации",
            "Есть только сканы инструкций",
            "Есть только листки вкладыши",
            "Нет фаркакодинамики",
            "Нет в ГРЛС",
        ]

        return res.status(200).json(statuses);
    }

    async GetAll(req, res){
        db.all(sqlRequests.GetAllDrugs(), [], (err, drugs) => {
            if (err || !drugs) {
              return res.status(404).json({ message: 'Ошибка при получении лекарственных средств' });
            }
            return res.status(200).json(drugs);
        });
    }

    async UpdateDrugsStatus(req, res){
        const {data} = req.body;
        
        if(data){
            data.forEach(element => {
                console.log(element)
                db.run(sqlRequests.UpdateDrugStatus(), [element.newStatus, element.drug_id], function (err) {
                    if (err || this.changes === 0) {
                        //console.error(err)
                      return res.status(400).json({ message: 'Ошибка обновления статуса задачи' });
                    }
                  });
            });

            return res.status(200).json({ message: 'Изменения в таблице успешно сохранены' });
        }
    }

    async UpdateDrugByID(req, res){
        const {id, drug_name, file, status, isDeleteFile} = req.body

        console.log(req.body)
        
        if(!id) return res.status(400).json({message:"Изменения неизвестного лекарственного средства"})
        if(!drug_name) return res.status(400).json({message:"Не указано название нового лекарственного средства"})

        const __filename = fileURLToPath(import.meta.url);
        const __dirname = path.dirname(__filename);

        if(req.files){ //Если пришел файл со схемой
            console.log('Получен файл для обновления')
            let fileName_json = uuid() + '.json';
            let filePath_json = path.resolve(__dirname, '..', '..','static','files', 'json', fileName_json)
            console.log(filePath_json)
            //Получение файла из исходголо заголовка
            let uploadedFile = req.files.file;
            let titleFile = uploadedFile.name
            console.log(titleFile)

            let titleArr =  titleFile.split(".")
            let graph_name =titleArr[0]; //Сохранение имени файла без расширения

            // Перемещаем файл json
            await new Promise((resolve, reject) => {
                uploadedFile.mv(filePath_json, function(err) {
                    if (err) reject(err);
                    else resolve();
                });
            });

            let fileName_html = uuid() + '.html';
            let filePath_html = path.resolve(__dirname,'..', '..','static','files', 'html', fileName_html)

            //Читаем файл и формируем html
            await fs.readFile(filePath_json, 'utf8', async (err, data) => {
                if (err) {
                    console.error(`Ошибка при чтении файла ${file}:`, err);
                    return;
                }
                try {
                    // Парсинг JSON
                    const graphCopy = JSON.parse(data);

                    //Формирование html
                    CreateHTML(graphCopy, filePath_html);
                    console.log(`Формирование html успешно`)
                            
                } catch (parseError) {
                    console.error(`Ошибка при парсинге JSON в файле ${file}:`, parseError);
                }
            });

            //Удаление старых файлов json и html
            console.log(id)
            db.get(sqlRequests.GetDrug(), [id], function (err, drug) {
                if (err || !drug) {
                    console.error(err);
                    return res.status(400).json({ message: 'Ошибка при получении ЛС из базы данных' });
                }

                if(drug.graph_file_json && drug.graph_file_json!=null){
                    const filePath = path.join(__dirname, '..', '..','static','files', 'json', drug.graph_file_json);
                    //console.log(filePath)
                    // Удаляем файл
                    fs.unlink(filePath, (err) => {
                        if (err) {
                            if (err.code === 'ENOENT') {
                                return res.status(404).send('Файл не найден');
                            } else {
                                return res.status(500).send('Произошла ошибка при удалении файла');
                            }
                        }
                    });
                }

                if(drug.graph_file_html && drug.graph_file_html!=null){
                    const filePath = path.join(__dirname, '..', '..','static','files', 'html', drug.graph_file_html);
                    //console.log(filePath)
                    // Удаляем файл
                    fs.unlink(filePath, (err) => {
                        if (err) {
                            if (err.code === 'ENOENT') {
                                console.log(`Файла html для удаления нет на сервере`)
                                //return res.status(404).send('Файл не найден');
                            } else {
                                return res.status(500).send('Произошла ошибка при удалении файла');
                            }
                        }
                    });
                }
           
                //Обновление файла со схемой графа
                //const drugName = drug_name.toUpperCase();
                db.run(sqlRequests.UpdateDrugFile(), [graph_name, fileName_json, fileName_html, id], function (err) {
                    if (err || this.changes === 0) {
                        console.error(err);
                        return res.status(400).json({ message: 'Ошибка при обновлении файла графа лекарственного средсва' });
                    }
                    else return res.status(200).json({ message: `Файл для лекарственного срадства ${drug_name} добавлен` });
                });

            });

        }

    }

    async DeleteDrug(req, res){
        const {id} = req.params

        console.log(id)

        db.get(sqlRequests.GetDrug(), [id], (err, drug) => {
            if (err || !drug) {
                //console.error(err);
                return res.status(404).json({ message: 'Лекарственное средство не существует' });
            }

            //console.log(drug)

            const __filename = fileURLToPath(import.meta.url);
            const __dirname = path.dirname(__filename);

            //Удаление файла с .json и .html
            if(drug.graph_file_json!=null){
                let filePath_json = path.resolve(__dirname, '..', '..','static','files', 'json', drug.graph_file_json)

                if (fs.existsSync(filePath_json)) {
                    fs.unlinkSync(filePath_json);
                } else {
                    res.status(404).send(`Файл схемы json не найден`);
                }
            }

            if(drug.graph_file_html!=null){
                let filePath_html = path.resolve(__dirname, '..', '..','static','files', 'html', drug.graph_file_html)

                if (fs.existsSync(filePath_html)) {
                    fs.unlinkSync(filePath_html);
                } else {
                    res.status(404).send(`Файл схемы html не найден`);
                }
            }

            //Удаление из базы данных
             db.run(sqlRequests.DeleteDrug(), [id], function (err) {
                if (err || this.changes === 0) {
                    return res.status(400).json({ message: 'Не удалось удалить лекарственное средства' });
                }
                return res.status(200).json({ message: 'Лекарственное средство удалено' });
            })
        });

       
    }

    async Export(req, res){
        let tempDir;
        try {
            // Создаем временную директорию
            tempDir = await fsExtra.mkdtemp(path.join(os.tmpdir(), 'my-app-'));//await fsExtra.tmpdir();
            const archiveName = 'MarkForInstructions.zip';
            //сonst archivePath = path.join(tempDir, archiveName);

            // Настройка ответа
            res.setHeader('Content-Type', 'application/zip');
            res.setHeader('Content-Disposition', `attachment; filename=${archiveName}`);

            // Создание архива
            const archive = archiver('zip', {zlib: { level: 9 },});

            //const output = fs.createWriteStream(archivePath);
            archive.pipe(res);

            archive.on('error', (err) => { throw err; });

            const __filename = fileURLToPath(import.meta.url);
            const __dirname = path.dirname(__filename);
            const staticDir = path.join(__dirname, '..', '..', 'static');

            // Добавляем папку css
            await addFilesToArchive(archive, path.join(staticDir, 'css'), 'models/css');
            // Добавляем папку js
            await addFilesToArchive(archive, path.join(staticDir, 'js'), 'models');


            //Добавляем файлы с html графами
            db.all(sqlRequests.GetAllDrugs(), [], async (err, drugs) => {
                if (err || !drugs) {
                    return res.status(404).json({ message: 'Ошибка при получении схем лекарственных средств' });
                }

                //Создание excel файла
                const wsData = [['№', 'ЛС', 'Состояние графа', 'Отображение графа']];  // Заголовки колонок
                drugs.forEach((drug, index)=>{
                    let newWsData = [(index+1), drug.drug_name, drug.status]
                    //Добавляем гиперссылку
                    if(drug.graph_file_html!=null){
                        const displayText = `${drug.graph_name}.html`
                        newWsData.push({
                            t: 's', 
                            v: displayText,
                            l: {Target: `./models/${drug.graph_name}.html`},
                            s: {
                                font: {
                                    color: { rgb: "7070E0" }, // Цвет текста (синий)
                                    sz: 12, // Размер шрифта
                                    underline: true, // Подчеркивание
                                    b: true, // Не жирный шрифт
                                    i: false // Не курсив
                                }
                            }
                        })
                    }else newWsData.push("")

                    wsData.push(newWsData)
                })

                 // Создаем книгу Excel
                 const ws = xlsx.utils.aoa_to_sheet(wsData);
                 const wb = xlsx.utils.book_new();
                 xlsx.utils.book_append_sheet(wb, ws, 'Drugs');
 
                 // Сохраняем Excel файл в временную папку
                 const excelFilePath = path.join(tempDir, 'ProcessOfInstructionsMarking.xlsx');
                 xlsx.writeFile(wb, excelFilePath);
 
                 // Добавляем Excel файл в архив
                 archive.file(excelFilePath, { name: 'ProcessOfInstructionsMarking.xlsx' });
                
                //Добавление файлов в архив
                for (const drug of drugs) {
                    if(drug.graph_file_html!=null){
                        const filePath = path.join(__dirname, '..', '..', 'static', 'files', 'html', drug.graph_file_html); // Путь к файлу из базы данных
                        if (fs.existsSync(filePath)) {
                            archive.file(filePath, { name: path.join('models', `${drug.graph_name}.html`) });
                        } else {
                            console.error(`Файл не найден: ${filePath}`);
                        }
                    }
                }

                await archive.finalize();
            });

        } catch (error) {
            console.error('Ошибка:', error);
            res.status(500).send('Ошибка при создании архива');
        }
    }
}
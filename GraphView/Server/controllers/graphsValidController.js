const db = require('../db/db.js')
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const ObjectsToCsv = require('objects-to-csv');
const archiver = require('archiver');

class graphsValidController {
    //Добавление новой проверки
    async AddNew(req, res){
        const {data, graph_id} = req.body

        console.log(req.body)

        //Проверки входных данных
        if(data.length===0) return res.status(500).json({message:"Нет данных о проверки"})
        if(!graph_id) return res.status(500).json({message:"Нет id графа"})

        let result = await db.GetByIdGraphSchema([graph_id])
        console.log(result)
        if(!result.rowCount) return res.status(500).json({message:"Граф с таким id не существует"})
    
        //Создание имени файла
        let fileName = uuidv4() + '.json'
        console.log(`fileName = ${fileName}`)

        let filePath = path.resolve(__dirname,'..','files','graphsValid', fileName)
        console.log(`filePath = ${filePath}`)

        const timestamp = new Date();

        //Создание файла json
        fs.writeFile(filePath, data, 'utf8', (err) => {
            if (err) {
                console.error('Ошибка записи файла:', err.stack);
                return res.status(500).json({data: 'Ошибка записи файла'})
            }
        });

        const title = `Проверка графа от ${timestamp}`

        //Сохранение данных в БД
        try{
            const result = await db.AddNewGraphsValid([graph_id, fileName, title, timestamp, timestamp]);
            return res.status(200).json({data:'Новые результаты проверки графа добавлены'})
        }
        catch(err){
            console.error('Ошибка при добавлении данных:', err.stack);
            return res.status(200).json({data: 'Ошибка при добавлении данных:', err: err.stack})
        }

    }

    //Получние всех проверок для схемы
    async GetAll(req, res){
        const {id} = req.params

        if(!id) return res.status(500).json({message:"Нет id графа"})

        let result = await db.GetByIdGraphSchema([id])
        if(!result.rowCount) return res.status(500).json({message:"Граф с таким id не существует"})

        try {
            const result = await db.GetAllGraphsValid([id]);
            return res.status(200).json({Data: result.rows})
            
        } catch (error) {
            console.error('Что-то пошло не так', error.stack);
            res.status(500).json({ message: 'Что-то пошло не так' })
        }

    }

    //Получение проверки по Id
    async GetById(req, res){
        const {id} = req.params

        if(!id) return res.status(500).json({message:"Нет id графа"})

        try {
            const result = await db.GetByIdGraphsValid([id]);
            let fileName = result.rows[0] ? result.rows[0].file_name : null;

            if(fileName){
                // Определяем путь к файлу
                let filePath = path.resolve(__dirname,'..','files','graphsValid', fileName)

                // Чтение файла асинхронным способом
                fs.readFile(filePath, 'utf8', (err, data) => {
                    if (err) {
                        console.error('Ошибка при чтении файла:', err);
                        return res.status(500).json({message:"Ошибка при чтении файла"})
                    }

                    try {
                        const jsonData = JSON.parse(data);
                        return res.status(200).json({Data: jsonData})

                    } catch (parseErr) {
                        console.error('Ошибка при парсинге JSON:', parseErr);
                        return res.status(500).json({message: parseErr})
                    }
                });

            }else return res.status(500).json({ message: 'Файл схемы не найден' })
            
        } catch (error) {
            console.error('Что-то пошло не так', error.stack);
            res.status(500).json({ message: 'Что-то пошло не так' })
        }
    }

    //Удаление проверки
    async DeleteById(req, res){
        const {id} = req.params

        if(!id) return res.status(500).json({message:"Нет id графа"})

        //Удаление с сервера
        let result = await db.GetByIdGraphsValid([id])
        let fileName = result.rows[0] ? result.rows[0].file_name : null;

        let filePath = path.resolve(__dirname,'..','files','graphsValid', fileName)

        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
            res.status(200).send(`Файл схемы удален`);
        } else {
            res.status(404).send(`Файл схемы не найден`);
        }

        //Удаление из БД
        result = await db.DeleteByIdGraphValid([id])

        return res.status(200).json({ message: 'Файл схемы удален' })
    }

    //Скачать проверку в форматах json/csv
    async DownloadById(req, res){
        try{
            const {id} = req.params
            const {format} = req.body

            if(!id) return res.status(500).json({ message: 'Некорректный id файла проверки схемы' })

            //Получем из бд название файла и выдаем ошибку если файла нет
            let result = await db.GetByIdGraphsValid([id])
            let fileName = result.rows[0] ? result.rows[0].file_name : null;
            console.log(result.rows[0])
            
            if(fileName){
                // Определяем путь к файлу
                let filePath = path.resolve(__dirname,'..','files','graphsValid', fileName)
                
                switch (format) {
                    case 'csv': // Экспорт в CSV
                        // Чтение файла асинхронным способом
                        fs.readFile(filePath, 'utf8', async (err, data) => {
                            if (err) {
                                console.error('Ошибка при чтении файла:', err);
                                return res.status(500).json({message:"Ошибка при чтении файла"})
                            }

                            try {
                                const jsonData = JSON.parse(data);
                                const csv = new ObjectsToCsv(jsonData);
                                const csvData = await csv.toString();

                                res.header('Content-Type', 'text/csv');
                                res.attachment('graphvalid.csv');
                                res.send(csvData);

                            } catch (parseErr) {
                                console.error('Ошибка при парсинге JSON:', parseErr);
                                return res.status(500).json({message: parseErr})
                            }
                        });
                        break;

                    default: //автоматом json
                        return res.sendFile(filePath)
                }
            }

        }catch (error) {
            console.error('Что-то пошло не так', error.stack);
            res.status(500).json({ message: 'Что-то пошло не так' })
        }
    }

    //Доделать!!!!
    async DownloadAll(req, res){
        try {
            const {id} = req.params
            if(!id) return res.status(500).json({ message: 'Некорректный id файла проверки схемы' })

            let result = await db.GetAllGraphsValid([id])
            if(!result.rowCount){
                return res.status(500).json({ message: 'Нет файлов для скачивания' })
            }

            const archive = archiver('zip', {
                zlib: { level: 9 } // Уровень сжатия
            });

            res.attachment('files.zip');
            archive.pipe(res);

             // Добавление файлов в архив
            const files = []         
            result.rows.forEach((record)=>{
                let fileName = record ? record.file_name : null;
                let filePath = path.resolve(__dirname,'..','files','graphsValid', fileName)
                files.push(filePath)
            })

            files.forEach(file => {
                archive.file(file, { name: path.basename(file) });
            });

            archive.finalize();


            
        } catch (error) {
            console.error('Что-то пошло не так', error.stack);
            res.status(500).json({ message: 'Что-то пошло не так' })
        }
    }
}

module.exports = new graphsValidController();
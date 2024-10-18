const db = require('../db/db.js')
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

class GraphsController{
    //Добавление новой схемы графа
    async AddNew(req, res){
        const {typeData} = req.body

        //console.dir(req)
        
        if(!typeData) return res.status(500).json({message:"Некорректное указание типа входных данных"})
        console.log(`typeData - ${typeData}`)

        //Создание имени файла
        let fileName = uuidv4() + '.json'
        console.log(`fileName = ${fileName}`)

        let filePath = path.resolve(__dirname,'..','files','graphs', fileName)
        console.log(`filePath = ${filePath}`)

        let titleFile = ''

        const timestamp = new Date();

        //Сохранение файлы на сервере
        switch (typeData) {
            case 'file':
                //Сохранение файла на сервер
                if (!req.files || Object.keys(req.files).length === 0) return res.status(500).send('Нет файлов для загрузки.');

                let uploadedFile = req.files.file;

                //Получение имени файла
                titleFile = uploadedFile.name

                // Перемещаем файл
                uploadedFile.mv(filePath, function(err) {
                    if (err) return res.status(500).send(err);
                });

                try{
                    const result = await db.addNewGraphSchema([fileName, timestamp, timestamp, titleFile]);
                    return res.status(200).json({data:'Новая схема графа добавлена'})
                }
                catch(err){
                    console.error('Ошибка при добавлении данных:', err.stack);
                    return res.status(200).json({data: 'Ошибка добавления файла'})
                }

            case 'textData':
                //Создание файла для хранения данных
                console.dir(req.body)
                const {data, title} = req.body

                if(!data) return res.status(500).json({data: 'Незаполненные данные'})
                if(!title) return res.status(500).json({data: 'Не указан заголовок'})
                else titleFile = title

                //Сделать проверку на соответствие входных данных шаблону JSON

                fs.writeFile(filePath, data, 'utf8', (err) => {
                    if (err) {
                        console.error('Ошибка записи файла:', err.stack);
                        return res.status(500).json({data: 'Ошибка записи файла'})
                    }
                });

                //Сохранение данных в БД
                try{
                    const result = await db.addNewGraphSchema([fileName, timestamp, timestamp, titleFile]);
                    return res.status(200).json({data:'Новая схема графа добавлена'})
                }
                catch(err){
                    console.error('Ошибка при добавлении данных:', err.stack);
                    return res.status(200).json({data: 'Ошибка добавления файла'})
                }

                //return res.send('Новая схема графа добавлена');
        
            default:
                return res.status(500).json({message:"Некорректное указание типа входных данных"})
        }
    }

    //Получение всех схем графа
    async GetAll(req, res){
        //console.log(`Запрос на получение всех данных`)
        try {
            const result = await db.getAllGraphSchemas();
            //console.dir(result)
            return res.status(200).json({Data: result.rows})
            
        } catch (error) {
            console.error('Что-то пошло не так', error.stack);
            res.status(500).json({ message: 'Что-то пошло не так' })
        }
        
    }

    //Получение схемы графа по id
    async GetById(req, res){
        try {
            const {id} = req.params

            if(!id) return res.status(500).json({ message: 'Некорректный id файла' })

            //Получем из бд название файла и выдаем ошибку если файла нет
            let result = await db.GetByIdGraphSchema([id])
            let fileName = result.rows[0] ? result.rows[0].file_name : null;
            console.log(result.rows[0])
            
            if(fileName){
                // Определяем путь к файлу
                let filePath = path.resolve(__dirname,'..','files','graphs', fileName)

                // Чтение файла асинхронным способом
                fs.readFile(filePath, 'utf8', (err, data) => {
                    if (err) {
                        console.error('Ошибка при чтении файла:', err);
                        return res.status(500).json({message:"Ошибка при чтении файла"})
                    }

                    try {
                        const jsonData = JSON.parse(data);
                        return res.status(200).json({Data: {schema: jsonData, title: result.rows[0].title}})

                    } catch (parseErr) {
                        console.error('Ошибка при парсинге JSON:', parseErr);
                        return res.status(500).json({message: parseErr})
                    }
                });

            }else return res.status(500).json({ message: 'Файл схемы не найден' })

        } catch (err) {
            console.error('Что-то пошло не так', err.stack);
            res.status(500).json({ message: 'Файл схемы не найден' })
        }
    }

    //Удаление схемы графа по id
    async DeleteById(req, res){
        try {
            const {id} = req.params

            if(!id) return res.status(500).json({ message: 'Некорректный id файла схемы' })
            
            //Удаление с сервера
            let result = await db.GetByIdGraphSchema([id])
            let fileName = result.rows[0] ? result.rows[0].file_name : null;

            let filePath = path.resolve(__dirname,'..','files','graphs', fileName)

            if (fs.existsSync(filePath)) {
                fs.unlinkSync(filePath);
                res.status(200).send(`Файл схемы удален`);
            } else {
                res.status(404).send(`Файл схемы не найден`);
            }

            //Удаление из БД
            result = await db.DeleteByIdGraphSchema([id])

            return res.status(200).json({ message: 'Файл схемы удален' })

        } catch (error) {
            console.error('Что-то пошло не так', error.stack);
            res.status(500).json({ message: 'Что-то пошло не так' })
        }
    }

    async DownloadById(req, res){
        try{
            const {id} = req.params

            if(!id) return res.status(500).json({ message: 'Некорректный id файла схемы' })

            //Получем из бд название файла и выдаем ошибку если файла нет
            let result = await db.GetByIdGraphSchema([id])
            let fileName = result.rows[0] ? result.rows[0].file_name : null;
            console.log(result.rows[0])
            
            if(fileName){
                // Определяем путь к файлу
                let filePath = path.resolve(__dirname,'..','files','graphs', fileName)

                res.sendFile(filePath)
            }

        }catch (error) {
            console.error('Что-то пошло не так', error.stack);
            res.status(500).json({ message: 'Что-то пошло не так' })
        }
    }
}

module.exports = new GraphsController();
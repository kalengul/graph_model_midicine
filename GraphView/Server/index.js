const express = require('express')
const cors = require('cors')

require('dotenv').config()
const path = require('path')
const fileUpload = require('express-fileupload')

const PORT = process.env.PORT||5000; //Полчуение значения порта
const app = express(); //Объект представляющий приложениеы
const db = require('./db/db.js')
//Конвейер обраотки запросов
app.use(cors({
      credentials: true,
      origin: ["http://localhost:3000"],
      optionsSuccessStatus: 200
    })
);
app.use(express.json({ extended: true }))
app.use(express.static(path.resolve(__dirname,'files/graphs'))) //Доступ к статическим файлам c графами
app.use(express.static(path.resolve(__dirname,'files/graphsValid'))) //Доступ к статическим файлам c графами
app.use(express.static('public'))
app.use(fileUpload({}))
app.use('/api', require('./routes/routes.js'))

app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

//app.get('/', (req, res)=>{res.status(200).json({message: 'WORKING'})})

//Старт сервера
const startApp = async()=>{
    try {
        //Создание таблиц
        db.createTables();
        console.log('Подключение к базе данных успешно:');

        app.listen(PORT, ()=>console.log(`Server start on port ${PORT}`))

    } catch (error) {
        console.log(error)

        //Разрыв подключения к БД
        process.on('SIGINT', () => {
            db.end(() => {
                console.log('Подключение к базе данных закрыто');
                process.exit(0);
            });
        });
    }
}

startApp()
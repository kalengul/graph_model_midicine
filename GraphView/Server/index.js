const express = require('express')
const cors = require('cors')

require('dotenv').config()

const PORT = process.env.PORT||5000; //Полчуение значения порта
const app = express(); //Объект представляющий приложениеы
//Конвейер обраотки запросов
app.use(cors({
      credentials: true,
      origin: ["http://localhost:3000"],
      optionsSuccessStatus: 200
    })
);
app.use(express.json({ extended: true }))
app.use('/api', require('./routes/routes.js'))

//Старт сервера
const startApp = async()=>{
    try {
        app.listen(PORT, ()=>console.log(`Server start on port ${PORT}`))
    } catch (error) {
        console.log(error)
    }
}

startApp()
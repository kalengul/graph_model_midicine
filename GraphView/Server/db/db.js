const { Pool } = require('pg');
const SqlRequests = require('./sqlRequests');

pool = new Pool({
    user: Central_Storage, // process.env.DB_USER,
    host: postgres, //process.env.DB_HOST,
    database: userpg, //process.env.DB_NAME,
    password: localhost, //process.env.DB_PASSWORD,
    port: 5432, //process.env.DB_PORT,
});

module.exports = {
    //Создание таблиц
    createTables: ()=>{
        pool.query(SqlRequests.sql_CreateTbale_Graphs_Models())
        pool.query(SqlRequests.sql_CreateTbale_Graphs_Valid())
    },

    //Запросы к таблице со схемами графа
    addNewGraphSchema: (params) => pool.query(SqlRequests.sql_INSERT_Graphs_Models(), params),
    getAllGraphSchemas: () => pool.query(SqlRequests.sql_SELECT_ALL_Graphs_Models()),
    GetByIdGraphSchema: (params) => pool.query(SqlRequests.sql_SELECT_BY_ID_Graphs_Models(), params),
    DeleteByIdGraphSchema: (params) => pool.query(SqlRequests.sql_DELETE_BY_ID_Graphs_Models(), params), //Добавить чтобы вместе с графом удалялись и все файлы с его проверками !!!!!!

    //Обращение к таблице с проверками графа
    AddNewGraphsValid: (params) => pool.query(SqlRequests.sql_INSERT_Graphs_Valid(), params),
    GetAllGraphsValid: (params) => pool.query(SqlRequests.sql_SELECT_ALL_Graphs_Valid(), params),
    GetByIdGraphsValid: (params) => pool.query(SqlRequests.sql_SELECT_BY_ID_Graphs_Valid(), params),
    DeleteByIdGraphValid: (params) => pool.query(SqlRequests.sql_DELETE_BY_ID_Graphs_Valid(), params),
};

class SqlRequests {
    ////
    /// graphs_models
    ////
    //Создание таблицы с моделями графа
    sql_CreateTbale_Graphs_Models(){
         return`
            CREATE TABLE IF NOT EXISTS graphs_models (
                id SERIAL PRIMARY KEY,
                file_name TEXT NOT NULL,
                create_data TIMESTAMP NOT NULL,
                update_data  TIMESTAMP NOT NULL,
                title TEXT NOT NULL
            );
        `
    }
    //Добавление новой схемы графа
    sql_INSERT_Graphs_Models(){
        return `INSERT INTO Graphs_Models (file_name, create_data, update_data, title) VALUES ($1, $2, $3, $4) RETURNING *`
    }

    //Полчуение всех схем графов
    sql_SELECT_ALL_Graphs_Models(){
        return `SELECT id, create_data, title FROM Graphs_Models`
    }

    //Получение схемы по ID
    sql_SELECT_BY_ID_Graphs_Models(){
        return `SELECT file_name, title from Graphs_Models WHERE id = $1`
    }

    //Удаленмие схемы по ID
    sql_DELETE_BY_ID_Graphs_Models(){
        return `DELETE FROM Graphs_Models WHERE id = $1`
    }


    ////
    /// graphs_valid
    ////
    //Создание таблицы с файлами проверки
    sql_CreateTbale_Graphs_Valid(){
        return ` 
            CREATE TABLE IF NOT EXISTS graphs_valid (
                id SERIAL PRIMARY KEY,
                graph_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                title TEXT NOT NULL,
                create_data TIMESTAMP NOT NULL,
                update_data  TIMESTAMP NOT NULL,
                FOREIGN KEY (graph_id) REFERENCES Graphs_Models(id) ON DELETE CASCADE
            );
        `
    }
    //Добавление файла с проверкой графа
    sql_INSERT_Graphs_Valid(){
        return `INSERT INTO graphs_valid (graph_id, file_name, title, create_data, update_data) VALUES ($1, $2, $3, $4, $5) RETURNING *`
    }
    //Полчуение всех проверок графа
    sql_SELECT_ALL_Graphs_Valid(){
        return `SELECT * FROM graphs_valid WHERE graph_id = $1`
    }
    //Полчуение провероки графа по ID
    sql_SELECT_BY_ID_Graphs_Valid(){
        return `SELECT * from graphs_valid WHERE id = $1`
    }
    //Удаленмие схемы по ID
    sql_DELETE_BY_ID_Graphs_Valid(){
        return `DELETE FROM graphs_valid WHERE id = $1`
    }

}

module.exports = new SqlRequests();
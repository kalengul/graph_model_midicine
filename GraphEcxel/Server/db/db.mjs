import sqlite3 from 'sqlite3';
import path from "path";
import { fileURLToPath } from "url";

//const sqlite3 = require('sqlite3').verbose();

// Получаем путь к текущему файлу
const __filename = fileURLToPath(import.meta.url);
// Получаем путь к текущей директории
const __dirname = path.dirname(__filename);

const db_name = path.join(__dirname, './database.db');

// Создаем/подключаемся к базе данных
const db = new sqlite3.Database(db_name, (err) => {
  if (err) {
    return console.error(err.message);
  }
  console.log('Connected to the SQLite database.');
});

db.serialize(async () => {
    const sql_CreateTbale_MarkForInstructions = `
      CREATE TABLE IF NOT EXISTS marks_for_instructions (
        id INTEGER PRIMARY KEY,
        drug_name TEXT,
        status TEXT, 
        graph_name TEXT,
        graph_file_json TEXT,
        graph_file_html TEXT
      );
    `;
    
    await db.run(sql_CreateTbale_MarkForInstructions);
});

export default db;
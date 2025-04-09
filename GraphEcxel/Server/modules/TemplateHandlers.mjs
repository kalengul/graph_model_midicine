import handlebars from "handlebars"
import fs from "fs"
import path from "path";
import { fileURLToPath } from "url";

export class TemplateHandlers{
    async compileTemplate(fileName, data) {
        try {
            // Получаем путь к текущему файлу
            const __filename = fileURLToPath(import.meta.url);
            // Получаем путь к текущей директории
            const __dirname = path.dirname(__filename);
            
            //Чтение шаблона
            const templateString = fs.readFileSync(path.join(__dirname, "..", "templates", fileName), "utf-8")
            const template = handlebars.compile(templateString);
            return template(data);
        } catch (err) {
            console.error("Ошибка при компиляции шаблона:", err);
            throw err;
        }
    }
}
//module.exports = new TemplateHandlers()
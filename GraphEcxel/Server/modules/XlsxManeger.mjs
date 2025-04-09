import fs from "fs"
import path from "path";
import { fileURLToPath } from "url";
import xlsx from "xlsx"

export class XlsxManeger{

    constructor(fileName){
        this.fileName_xlsc = fileName
        this.workbook = xlsx.readFile(fileName)
        this.sheets = this.workbook.SheetNames

        this.savedHyperlinks = {};
    }

    CreateLinkDisplayText = (htmlFilePath) =>{
        const fileName = htmlFilePath.split('/')
        return fileName[fileName.length-1]
    }

    NormalizString(str){
        str = str.toLowerCase().trim(); //Преобразовани в нижний регистр иудаление пробелов в начале и в конце строки
        return str
    }

    AddHiperLink(htmlFilePath, stringId, sheetName){
        //console.log(htmlFilePath)
        const worksheet = this.workbook.Sheets[sheetName];

        if (!worksheet) {
            console.log(`Лист "${sheetName}" не найден в файле Excel.`);
            return;
        }

        //Сохраняем все гипер ссылки из файла
        const hyperlinks = [];

        for (const cellAddr in worksheet) {
            if (cellAddr[0] === '!') continue;

            if( Object.hasOwn(worksheet[cellAddr], "l")){
                hyperlinks.push({
                    cellAddr: cellAddr,
                    v: worksheet[cellAddr].v,
                    l: {
                        ref: worksheet[cellAddr].l.ref,
                        id: worksheet[cellAddr].l.id,
                        Target: worksheet[cellAddr].l.Target,
                        Rel: {
                            Type: worksheet[cellAddr].l.Rel.Type,
                            Target: worksheet[cellAddr].l.Rel.Target,
                            Id: worksheet[cellAddr].l.Rel.Id,
                            TargetMode: worksheet[cellAddr].l.Rel.TargetMode,
                        },
                    }
                })
            }
        }

        const data = xlsx.utils.sheet_to_json(worksheet, { header: 1 }); // Преобразуем лист в JSON
        //console.log(data)

        //Добавление гиперссылко на html
        const updatedData = data.map((row, index) => {
            if (index === 0) return row; // Пропускаем заголовок

            //Ищем ЛС для html
            if (this.NormalizString(stringId)===this.NormalizString(row[1])) {
                const displayText = `${this.CreateLinkDisplayText(htmlFilePath)}` 
                row[3] = { 
                    t: 's', 
                    v: displayText,
                    l: {Target: htmlFilePath},
                    s: {
                        font: {
                            color: { rgb: "7070E0" }, // Цвет текста (синий)
                            sz: 12, // Размер шрифта
                            underline: true, // Подчеркивание
                            b: true, // Не жирный шрифт
                            i: false // Не курсив
                        }
                    }
                }
            } else{
                //Проверяем есть ли сохраненные гиперссылки
                //console.log(hyperlinks.filter(e=> e.v === row[3]))
                let saveLink = hyperlinks.filter(e=> e.v === row[3])[0]
                //console.log(saveLink)
                if(row[3]!==undefined && saveLink!==undefined){
                    let updateLink = {
                        t: "s",
                        v: saveLink.v,
                        l: {
                            //ref: saveLink.l.ref,
                            //id: saveLink.l.id,
                            Target: saveLink.l.Target,
                            // Rel: {
                            //   Type: saveLink.l.Rel.Type,
                            //   Target: saveLink.l.Rel.Target,
                            //   Id: saveLink.l.Rel.Id,
                            //   TargetMode: saveLink.l.Rel.TargetMode
                            // }
                        },
                        s: {
                            font: {
                                color: { rgb: "7070E0" }, // Цвет текста (синий)
                                sz: 12, // Размер шрифта
                                underline: true, // Подчеркивание
                                b: true, // Не жирный шрифт
                                i: false // Не курсив
                            }
                        }

                    }

                    if(row.length==4) row[3] = updateLink
                    else row.push(updateLink);
                    
                    //console.log(saveLink)
                    
                    //row[3].
                    //console.log(hyperlinks[row[3]])
                }
            }

            return row;
        })

        //console.log(updatedData)

        // Преобразуем обновленные данные обратно в лист
        const updatedWorksheet = xlsx.utils.aoa_to_sheet(updatedData);
        this.workbook.Sheets[sheetName] = updatedWorksheet; //Обновляем лист
        xlsx.writeFile(this.workbook, this.fileName_xlsc);  //Сохраняем лист

        const worksheet1 = this.workbook.Sheets[sheetName];
        //console.log(worksheet1)
        
        // // Обрабатываем данные
        // const updatedData = data.map((row, index) => {
        //     if (index === 0) return row; // Пропускаем заголовок

        //     // Проверяем, существует ли HTML-файл
        //     if (this.NormalizString(stringId)===this.NormalizString(row[1])) {
        //         //console.log(row[1])
        //         const displayText = `${this.CreateLinkDisplayText(htmlFilePath)}` 
        //         //const cellAddress = xlsx.utils.encode_cell({ c: 3, r: index }); // Столбец D (индекс 3)
        //         //worksheet[cellAddress] = {//
        //         row[3] = { 
        //             t: 's', 
        //             v: displayText,
        //             l: {Target: htmlFilePath},
        //             s: {
        //                 font: {
        //                     color: { rgb: "7070E0" }, // Цвет текста (синий)
        //                     sz: 12, // Размер шрифта
        //                     underline: true, // Подчеркивание
        //                     b: true, // Не жирный шрифт
        //                     i: false // Не курсив
        //                 }
        //             }
        //         };
        //     }else{
        //         // Если файл не существует, оставляем поле пустым
        //         //row[3] = row[3];
        //         // let rowAdr = worksheet[xlsx.utils.encode_cell({ c: 3, r: index })]
        //         // if(rowAdr != undefined && Object.hasOwn(rowAdr, "l")){
        //         //     //console.log(rowAdr)
        //         //     row[3]={
        //         //         t: rowAdr.t,
        //         //         v: rowAdr.v,
        //         //         h: rowAdr.h,
        //         //         w: rowAdr.w,
        //         //         l: {
        //         //             ref: rowAdr.l.rowAdr,
        //         //             id: rowAdr.l.id,
        //         //             Target: rowAdr.l.Target,
        //         //             Rel: rowAdr.l.Rel,
        //         //         }
        //         //     }
        //         // }
        //     }
        //     return row;
        // })

        // // Преобразуем обновленные данные обратно в лист
        // const updatedWorksheet = xlsx.utils.aoa_to_sheet(updatedData);

        // // 4. Восстанавливаем гиперссылки в соответствующие ячейки
        // hyperlinks.forEach(({ cell, hyperlink }) => {
            
        //     if (!updatedWorksheet[cell]) {
        //         updatedWorksheet[cell] = {}; // Создаём пустую ячейку, если она была удалена
        //     }
        //     updatedWorksheet[cell].hyperlink = hyperlink;
        //     updatedWorksheet[cell].s = { font: { color: { rgb: "0000FF" } } }; // Делаем ссылку подчёркнутой (синяя)
        // });

        // console.log("///////////////////////////////////////////")
        // console.log(updatedWorksheet)
        // console.log("///////////////////////////////////////////")

        // //console.log(hyperlinks);

        // // Обновляем лист в книге
        // this.workbook.Sheets[sheetName] = updatedWorksheet;

        // // 3. Восстанавливаем гиперссылки
        // // Если структура листа не изменилась (адрес ячеек совпадает),
        // // для каждой сохранённой гиперссылки снова устанавливаем свойство l
        // for (const cellAddr in this.savedHyperlinks) {
        //     if (this.workbook.Sheets[cellAddr]) {
        //     worksheet[cellAddr].l = this.savedHyperlinks[cellAddr];
        //     }
        // }

        // // Сохраняем обновленный Excel-файл
        // xlsx.writeFile(this.workbook, this.fileName_xlsc);

        // console.log(this.savedHyperlinks)
    }
}
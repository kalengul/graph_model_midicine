export class SqlRequests{
    AddNewDrug(){
        const sql = `
            INSERT INTO marks_for_instructions (drug_name, status, graph_name, graph_file_json, graph_file_html) VALUES (?, ?, ?, ?,?)
        `;
        return sql
    }

    GetDrug(){
        const sql = `SELECT * FROM marks_for_instructions WHERE id = ?`
        return sql
    }

    GetAllDrugs(){
        const sql =`
            SELECT * FROM marks_for_instructions
        `;
        return sql
    }

    DeleteDrug(){
        const sql = `
            'DELETE FROM marks_for_instructions WHERE id = ?'
        `;
        return sql
    }

    UpdateDrugStatus(){
        const sql = `
            UPDATE marks_for_instructions SET status = ? WHERE id = ?;
        `
        return sql
    }

    UpdateDrugFile(){
        const sql = `
            UPDATE marks_for_instructions SET graph_name = ? , graph_file_json  =?, graph_file_html  =?  WHERE id = ?;
        `
        return sql
    }

    DeleteDrug(){
        const sql =` DELETE FROM marks_for_instructions WHERE id = ? `
        return sql
    }
}
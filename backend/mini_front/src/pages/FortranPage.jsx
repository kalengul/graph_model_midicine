import { useState } from "react";


export default function FortranPage() {
    const [fortranFile, setFortranFile] = useState(null);

    const handlerUpload = async () => {
        const formData = new FormData();
        if (fortranFile) formData.append("file", fortranFile);

        const response = await fetch("/api/v1/import_to_db/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        alert(data.result.message);
    };

    const handlerDownload = () => {
        window.location.href = "/api/v1/simple_export_from_db/";
    };

    return (
        <div className="form-page">
            <h2>Данные для Фортарана</h2>
            <label>Выберите файл с данными для Фортрана</label>
            <input accept=".xlsx" type="file" required onChange={(e) => setFortranFile(e.target.files[0])} />
            <div className="button-group">
                <button onClick={handlerUpload}>Загрузить</button>
                <button onClick={handlerDownload}>Скачать</button>
            </div>
        </div>
    )
}
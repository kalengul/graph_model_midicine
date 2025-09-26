import { useState } from "react";


export default function SynonymsPage() {
    const [synonymsFile, setSynonymsFile] = useState(null);

    const handlerUpload = async () => {
        const formData = new FormData();
        if (synonymsFile) formData.append("file", synonymsFile);

        const response = await fetch("/api/v1/import_synonyms/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        alert(data.result.message);
    };

    const handlerDownload = () => {
        window.location.href = "/api/v1/export_synonyms/";
    };

    return (
        <div className="form-page">
            <h2>Синонимы</h2>
            <label>Выберите файл с синонимами</label>
            <input accept=".json" type="file" required onChange={(e) => setSynonymsFile(e.target.files[0])}/>
            <div className="button-group">
                <button onClick={handlerUpload}>Загрузить</button>
                <button onClick={handlerDownload}>Скачать</button>
            </div>
        </div>
    )
}

import { useState } from "react";


export default function ContrasPage() {
    const [contraFile, setContraFile] = useState(null);

    const handlerUpload = async () => {
        const formData = new FormData();
        if (contraFile) formData.append("file", contraFile);

        const response = await fetch("/api/v1/contraindications/load_and_link/",{
            method: "POST",
            body: formData
        });

        const data = await response.json();
        alert(data.result.message);
    };

    const handlerDownload = () => {
        window.location.href = "/api/v1/contraindications/load_and_link/";
    };

    return (
        <div className="form-page">
            <h2>Противопоказания</h2>
            <label>Выберите файл с противопоказаниями</label>
            <input accept=".json" type="file" required onChange={(e) => setContraFile(e.target.files[0])} />
            <div className="button-group">
                <button onClick={handlerUpload}>Загрузить</button>
                <button onClick={handlerDownload}>Скачать</button>
            </div>
        </div>
    )
}

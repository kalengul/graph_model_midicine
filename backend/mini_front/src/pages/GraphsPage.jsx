import { useState } from "react";


export default function GraphsPage() {
    const [graphFile, setGraphFile] = useState(null);
    const [probFile, setProbFile] = useState(null);

    const handlerUpload = async () => {
        const formData = new FormData();
        if (graphFile) formData.append("graph_file", graphFile);
        if (probFile) formData.append("probability_file", probFile);

        const response = await fetch('/api/v1/graph/storage_graph/', {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        alert(data.result.message);
    };

    const handlerDownload = () => {
        window.location.href = "/api/v1/graph/storage_graph/";
    };

    return (
        <div className="form-page">
            <h2>Семантические графы</h2>
            <label>Выберите файл c графом</label>
            <input accept='.json' type="file" required onChange={(e) => setGraphFile(e.target.files[0])}/>
            <label>Выберите файл с вероятностями</label>
            <input accept='.json' type="file" required onChange={(e) => setProbFile(e.target.files[0])}/>
            <div className="button-group">
                <button onClick={handlerUpload}>Загрузить</button>
                <button onClick={handlerDownload}>Скачать</button>
            </div>
        </div>
    )
}

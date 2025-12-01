import { useState } from "react";


export default function BannedPairPage() {
    const [bannedPairFile, setBannedPairFile] = useState(null);

    const handlerUpload = async () => {
        const formData = new FormData();
        if (bannedPairFile) formData.append("file", bannedPairFile);

        const response = await fetch("/api/v1/import_banned_pair/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        alert(data.result.message);
    };

    return (
        <div className="form-page">
            <h2>Запрещённые комбинаций</h2>
            <label>Выберите файл запрещённых сочетаний лекарственных средств</label>
            <input type="file" accept=".csv" required onChange={(e) => setBannedPairFile(e.target.files[0])} />
            <div className="button-group">
                <button onClick={handlerUpload}>Загрузить</button>
            </div>
        </div>
    )
}

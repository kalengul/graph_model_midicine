import { useState } from 'react'
import './App.css'

export default function App() {
  const [graphFile, setGraphFile] = useState(null);
  const [probFile, setProbFile] = useState(null);

  const handlerUpload = async () => {
    const formData = new FormData();
    if (graphFile) formData.append("graph_file", graphFile);
    if (probFile) formData.append("probability_file", probFile);

    const response = await fetch("/api/v1/graphs/storage_graph/",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();
    alert(data.result.message);
  };

  const handlerDownload = () => {
    window.location.href = "/api/v1/graphs/storage_graph/";
  };

  return (
      <div className='form-box'>
        <h1>Загрузка/выгрузка <br/> семантического графа</h1>
        <div className='input-container'>
          <label htmlFor="for-graph">Выберите файл c графом</label>
          <input accept=".json" id="for-graph" type="file" required onChange={(e) => setGraphFile(e.target.files[0])}/>
          <br/>
          <label htmlFor="for-prob">Выберите файл с вероятностями</label>
          <input accept='.json' id="for-prob" type="file" required onChange={(e) => setProbFile(e.target.files[0])}/>
        </div>
        <br/>
        <div className='button-container'>
          <button className='button-load' onClick={handlerUpload}>Загрузить файлы</button>
          <button className='button-load' onClick={handlerDownload}>Скачать архив</button>
        </div>
      </div>
  );
}

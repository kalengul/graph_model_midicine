
import axios from 'axios'
import { saveAs } from 'file-saver';

export const StatisticBayesPage = () =>{
    const ExportHandler = async ()=>{
        try {
            await axios({method: "GET", 
                url: "/api/statisticFile", 
                responseType: 'arraybuffer',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`},//headers: {responseType: 'blob'},
            }) .then((res)=>{
                console.log(res)
                const blob = new Blob([res.data], { type: 'application/zip' });
                saveAs(blob, 'StatisticFile.zip');
            })     
        } catch (error) {
            console.error(error);
        }
    }

    return (
            <main className=" p-3 w-100">
                <h1>Статистика по работе сети Байеса</h1>
                <div className='mt-4'>
                    <button className='btn send-btn' onClick={ExportHandler}>Экспортировать</button>
                </div>
                
            </main>
    )
}
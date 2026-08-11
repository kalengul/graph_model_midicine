
import { useEffect, useState } from 'react';
import axios from 'axios'
import { saveAs } from 'file-saver';

import "./StatisticBayes.scss"
import moomi from "../../../public/moomitroll.png"

import { useAppDispatch, useAppSelector } from "../../redux/hooks"
import { fetchReportsList, createReport, cancelRunReport, updateRunReport } from "../../redux/CombinationCheckerSlice"
import { LoadBar } from "../../components/loadBar/loadBar";
import { CompleteStatus } from '../../components/completeStatus/completeStatus';

export const StatisticBayesPage = () =>{
    // Статистика по работе сети Байеса
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

    //Данные для запуска новой оценки рангов
    const [countCombin, setCountCombin] = useState<number>(2)

    const loadStatusReportsList = useAppSelector(state=>state.combinationChecker.loadStatusReportsList)
    const reportsList = useAppSelector(state=>state.combinationChecker.reports)
    const errNewReport = useAppSelector(state=>state.combinationChecker.errNewReport)
    const loadCreateNewReport = useAppSelector(state=>state.combinationChecker.loadCreateNewReport)
    const updateInfo = useAppSelector(state=>state.combinationChecker.updateInfo)
    console.log(loadCreateNewReport)
    const dispatch = useAppDispatch()
    useEffect(()=>{
        dispatch(fetchReportsList())
    }, [dispatch])

    //Создание нового отчета
    const CreateReportHandler = () =>{
        const reportName: string = ""
        dispatch(createReport({
            name: reportName,
            max_combination_size: countCombin,
            rank_name: "rang_base"
        }))

        dispatch(fetchReportsList())
    }

    //Отменить текщую оценку
    const CancelRunReportHandler = () => {
        dispatch(cancelRunReport())
    }

    //Обновить статус расчетов
    const UpdateRunReportHandler = () =>{
        dispatch(updateRunReport())
    }

    return (
            <main className=" p-3 w-100">
                <div>
                    <h1>Статистика по работе сети Байеса</h1>
                    <div className='mt-4'>
                        <button className='btn send-btn' onClick={ExportHandler}>Экспортировать</button>
                    </div>
                </div>
                <hr></hr>
                <div className='mt-5'>
                    <h1>Оценка корректности рангов</h1>
                    <div className='mt-2 combinationChecker-container'>
                    <div className='assesHistory-Block glass'>
                        <h6>История оценок</h6>
                        {
                            (loadStatusReportsList=="loading") ? <LoadBar className="mt-4"/>
                            :
                            (reportsList.length === 0) ? <p>Пока нет результатов оценок</p>
                            :
                            <div>
                            {reportsList.map((e, index)=>
                                <div className='flex jc-sb mt-1'>
                                    <div>
                                        <span className='me-2'>{index+1}</span>
                                        <span>{e.name} - {e.created_at}</span>
                                    </div>
                                    <div><CompleteStatus status={e.status}/></div>
                                </div>
                            )}
                            </div>

                        }
                    </div>
                    <div className='assesNew-Block glass'>
                        <h6>Запустить новую оценку</h6>
                        <div className='mb-2'>
                            <div>
                                <label className=' control-label me-4'>Выбирите количество комбинаций:</label>
                                <select className='form-select form-select-sm' value={countCombin} onChange={(e) => setCountCombin(Number(e.target.value))} >
                                    {[...Array(9).keys()].map(i => {
                                        const value = i + 2;
                                        return (
                                            <option key={value} value={value}>
                                            {value}
                                            </option>
                                        );
                                    })}
                                </select>
                            </div>
                            {countCombin > 5 && 
                            <div>
                                <p className='err'>Расчет оченки рангов может занимать длительное время <img className='MoomiIMG' src={moomi}/></p>
                            </div>}
                        </div>
                        
                        <button className='btn send-btn' onClick={CreateReportHandler}>Оценить</button>
                        { errNewReport && <div className='mt-3 errStart'>{errNewReport}</div>}
                        {(loadCreateNewReport=="loading") &&
                        <>
                            <hr></hr>
                            {updateInfo && <>
                                <div>
                                    <div>Название: {updateInfo.name}</div>
                                    <div>Максимальный размер комбинации: {updateInfo.max_combination_size}</div>
                                    <div>Версия файла весов: {updateInfo.weight_version_name}</div>
                                    <div>Проверено комбинаций: {updateInfo.checked_combinations}/{updateInfo.total_iterations}</div>
                                    <div>Прогесс: {updateInfo.progress}</div>
                                </div>
                                <hr></hr>
                            </>}
                            <div className='loadCreateNewRepoer-Block mt-3'>
                                <button className='btn second-btn' onClick={UpdateRunReportHandler}>Обновить статус</button>
                                <button className='btn second-btn' onClick={CancelRunReportHandler}>Отменить оценку</button>
                            </div>

                        </>
                        }
                    </div>
                    </div>
                </div>
                
            </main>
    )
}
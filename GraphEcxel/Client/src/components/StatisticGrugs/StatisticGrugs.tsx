import {useSelector} from 'react-redux';
 
function StatisticGrugs () {

    const drugsStatistic = useSelector(state=>state.drugs.drugsStatistic)
    console.log(drugsStatistic)
    return(
        <>
            {drugsStatistic && 
                <div className=' mb-3'>
                    <div className="flex align-center mb-2">
                        <label className='me-1'>Всего лекарственных средств:</label>
                        <span>{drugsStatistic.drugsCount}</span>
                    </div>
                    <div className="flex">
                        <div className='me-5'>
                            <div className="flex align-center">
                                <label className='me-1'>Статус 'Завершен':</label>
                                <span>{drugsStatistic.end}</span>
                            </div>


                            <div className="flex align-center">
                                <label className='me-1'>Статус 'В процессе':</label>
                                <span>{drugsStatistic.inProcess}</span>
                            </div>

                            <div className="flex align-center">
                                <label className='me-1'>Статус 'Недостаточно информации':</label>
                                <span>{drugsStatistic.noInfo}</span>
                            </div>

                            <div className="flex align-center">
                                <label className='me-1'>Статус 'Есть только сканы инструкций':</label>
                                <span>{drugsStatistic.onlyScan}</span>
                            </div>
                        </div>
                        <div>
                            <div className="flex align-center">
                                <label className='me-1'>Статус 'Есть только листки вкладыши':</label>
                                <span>{drugsStatistic.onlyInsertList}</span>
                            </div>

                            <div className="flex align-center">
                                <label className='me-1'>Статус 'Нет фаркакодинамики':</label>
                                <span>{drugsStatistic.noFarcodynamics}</span>
                            </div>

                            <div className="flex align-center">
                                <label className='me-1'>Статус 'Нет в ГРЛС':</label>
                                <span>{drugsStatistic.noGRLS}</span>
                            </div>
                        </div>
                    </div>
                </div>
            }
        </>
    )
 }

 export default StatisticGrugs
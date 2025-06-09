import { useEffect, useState } from "react"
import {AddSideEffectForm} from "../addSideEffectForm/addSideEffectForm"
import { SideEffectsTable } from '../sideEffectsTable/sideEffectsTable'

import trash3 from "../../../public/trash3.svg"
import chevronRight from "../../../public/chevron-right.svg"
import { ErrMessageCard } from '../messageCards/errMessageCard';
import { Modal } from '../modals/modal';
import { ModalNotification } from "../modals/modalNotification"
import "./sideEffectManage.scss"

import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import { fetchSideEffectList, fetchSideEffectRankList, updateSideEffectRankList, deleteSideEffect, exportRanksFile} from '../../redux/SideEffectManageSlice'



export const SideEffectManage = () =>{
    const dispatch = useAppDispatch()

    useEffect(()=>{
        Promise.all([
            dispatch(fetchSideEffectList()),
            dispatch(fetchSideEffectRankList())
        ]);
    }, [dispatch])

    const SideEffectList = useAppSelector((state)=>state.sideEffectManage.sideEffects)
    const updateRangs = useAppSelector((state)=>state.sideEffectManage.updateRanksList)


    const [UpdateNotification, setUpdateNotification] = useState({
        isVisible: false, type: "", message: ""
    })
    const saveSideEffectChanges = async ()=>{
        const resultAction = await dispatch(updateSideEffectRankList(updateRangs))
        if (updateSideEffectRankList.fulfilled.match(resultAction)) {
            setUpdateNotification({isVisible: true, type: "success", message: "Ранги обновлены"})
        }
        else setUpdateNotification({isVisible: true, type: "error", message: "Ошибка при обновлении рангов"})
    }

    const deleteSideEffectHendler=(id: string) =>{
        dispatch(deleteSideEffect(id))
    }

    const [isVisible, setIsVisible] = useState<string | null>(null)

    return (
        <>
         <div className="w-100 mt-4 drugManage">
            <a className='link-dark' data-bs-toggle="collapse" href="#collapseSETable" role="button" aria-expanded="false" aria-controls="collapseSETable">
                <div className="flex ai-center">
                    <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                    <h4>Таблица побочных эффектов с рангами</h4>
                    
                </div>
            </a>
            <div className="collapse mt-4" id="collapseSETable">
                <SideEffectsTable/>
                <div className="flex jc-sb">
                    <div>
                        <button className='btn send-btn mt-3' onClick={saveSideEffectChanges}>Сохранить изменения</button>
                        {UpdateNotification.isVisible && 
                            <ModalNotification 
                                type={UpdateNotification.type} 
                                message={UpdateNotification.message}
                                onClose={() => setUpdateNotification({...UpdateNotification, isVisible: false})}
                            />
                        }
                    </div>
                    <div className="flex">
                        <button className='btn send-btn mt-3 me-3'>Загрузить ранги</button>
                        <button className='btn send-btn mt-3' onClick={()=>{dispatch(exportRanksFile())}}>Экспортировать ранги</button>
                    </div>
                </div>
            </div>
        </div>
        <hr/>

        <div className="w-75 mt-4 drugManage">
            <a className='link-dark' data-bs-toggle="collapse" href="#collapseSideEffect" role="button" aria-expanded="false" aria-controls="collapseSideEffect">
                <div className="flex ai-center">
                    <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                    <h4>Добавить побочный эффект</h4>
                </div>
            </a>
            <div className="collapse mt-4" id="collapseSideEffect">
                <AddSideEffectForm/>
            </div>
        </div>
        
        <div className="w-100 mt-4 drugManage">
            <a className='link-dark' data-bs-toggle="collapse" href="#collapseGetDrug" role="button" aria-expanded="false" aria-controls="collapseGetDrug">
                <div className="flex ai-center">
                    <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                    <h4>Список побочных эффектов</h4>
                    
                </div>
            </a>
            <div className="collapse mt-4" id="collapseGetDrug">
                {Array.isArray(SideEffectList) ? ( SideEffectList.length > 0 ? SideEffectList.map((sideEffect, index)=>
                <>
                    <div className='flex jc-sb w-100 ps-3 pe-3' key={sideEffect.id}>
                        <div>
                            <span className='me-3'>{index+1}.</span> 
                            <span>{sideEffect.se_name}</span>
                        </div>
                        <img src={trash3} onClick={()=>{setIsVisible(`se-${sideEffect.id}`)}}/>
                        <Modal 
                            id = {`se-${sideEffect.id}`} 
                            isVisible={isVisible===`se-${sideEffect.id}`} 
                            onClose={()=>setIsVisible(null)}
                            handler={()=>{deleteSideEffectHendler(sideEffect.id)}}
                            message={`Вы хотите удалить лекарственное средство ${sideEffect.se_name}?`}
                        ></Modal>
                    </div>
                    <hr/>
                </>
                ): <ErrMessageCard message='Нет Добавленных побочных эффектов'/>)
                :
                <ErrMessageCard message="Не удалось получить список побочных эффектов. Пожалуйста, перезагрузите страницу или попробуйте позже"/>
                }
            </div>
        </div>
       
    </>
    )
}
import { useEffect } from "react"
import {AddDrugGroupForm} from "../addSideEffectForm/addSideEffectForm"
import { SideEffectsTable } from '../sideEffectsTable/sideEffectsTable'

import trash3 from "../../../public/trash3.svg"
import chevronRight from "../../../public/chevron-right.svg"
import { ErrMessageCard } from '../messageCards/errMessageCard';
import "./sideEffectManage.scss"

import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import { initStates, fetchSideEffectList, fetchSideEffectRankList, updateSideEffectRankList} from '../../redux/SideEffectManageSlice'


export const SideEffectManage = () =>{
    const dispatch = useAppDispatch()

    useEffect(()=>{
        dispatch(initStates())
        dispatch(fetchSideEffectList())
        dispatch(fetchSideEffectRankList())
    }, [dispatch])

    const SideEffectList = useAppSelector((state)=>state.sideEffectManage.sideEffects)

    const updateRangs = useAppSelector((state)=>state.sideEffectManage.updateRanksList)
    const saveSideEffectChanges=()=>{
        dispatch(updateSideEffectRankList(updateRangs))
    }

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
              <button className='btn send-btn mt-3' onClick={saveSideEffectChanges}>Сохранить изменения</button>
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
                <AddDrugGroupForm/>
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
                        <img src={trash3}/>
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
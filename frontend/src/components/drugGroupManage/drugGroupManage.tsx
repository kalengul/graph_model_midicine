import { useEffect } from 'react'

import chevronRight from "../../../public/chevron-right.svg"
import trash3 from "../../../public/trash3.svg"
import { AddDrugGroupForm} from '../../components/addDrugGroupForm/addDrugGroupForm';
import { ErrMessageCard } from '../messageCards/errMessageCard';

import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import { fetchDrugGroupList , deleteDrugGroup} from '../../redux/DrugGroupManageSlice';
import {initStates} from '../../redux/DrugGroupManageSlice'



export const DrugGroupManage = () =>{
    const dispatch = useAppDispatch()
    useEffect(()=>{
        dispatch(initStates())
        dispatch(fetchDrugGroupList())
    }, [dispatch])

    const drugGroupList = useAppSelector((state)=>state.drugGroupManage.drugGroups)

    const deleteDrugGroupHendler = (id: string) =>{
        dispatch(deleteDrugGroup(id))
    }

    return(
        <>
            <div className="w-75 mt-4 drugManage">
                <a className='link-dark' data-bs-toggle="collapse" href="#collapseAddDrugGroup" role="button" aria-expanded="false" aria-controls="collapseAddDrugGroup">
                    <div className="flex ai-center">
                        <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                        <h4>Добавить группу лекарственных средств</h4>
                    </div>
                </a>
                <div className="collapse mt-4" id="collapseAddDrugGroup">
                    <AddDrugGroupForm/>
                </div>
            </div>
            <hr/>

            <div className="w-100 mt-4 drugManage">
                <a className='link-dark' data-bs-toggle="collapse" href="#collapseGetDrugGroup" role="button" aria-expanded="false" aria-controls="collapseGetDrugGroup">
                    <div className="flex ai-center">
                        <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                        <h4>Список групп лекарственных средств</h4>
                        
                    </div>
                </a>
                <div className="collapse mt-4" id="collapseGetDrugGroup">
                    {Array.isArray(drugGroupList) ? ( drugGroupList.length > 0 ? drugGroupList.map((drugGroup, index)=>
                    <>
                        <div className='flex jc-sb w-100 ps-3 pe-3' key={drugGroup.id}>
                            <div>
                                <span className='me-3'>{index+1}.</span> 
                                <span>{drugGroup.dg_name}</span>
                            </div>
                            <img src={trash3} onClick={()=>{deleteDrugGroupHendler(drugGroup.id)}}/>
                        </div>
                        <hr/>
                    </>
                    ) : <ErrMessageCard message='Нет добавленных групп лекарственных средств'/>)
                    : 
                    <ErrMessageCard message='Не удалось получить список групп лекарственных средств. Пожалуйста, перезагрузите страницу или попробуйте позже'/>
                    }
                </div>
            </div>
        </>
    )
}
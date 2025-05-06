import { useEffect, useState } from 'react'

import chevronRight from "../../../public/chevron-right.svg"
import trash3 from "../../../public/trash3.svg"
import { AddDrugGroupForm} from '../../components/addDrugGroupForm/addDrugGroupForm';
import { ErrMessageCard } from '../messageCards/errMessageCard';

import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import { fetchDrugGroupList , deleteDrugGroup} from '../../redux/DrugGroupManageSlice';
import { Modal } from '../modals/modal';


export const DrugGroupManage = () =>{
    const dispatch = useAppDispatch()
    useEffect(()=>{
        dispatch(fetchDrugGroupList())
    }, [dispatch])

    const drugGroupList = useAppSelector((state)=>state.drugGroupManage.drugGroups)

    const deleteDrugGroupHendler = (id: string) =>{
        dispatch(deleteDrugGroup(id))
    }

    const [isVisible, setIsVisible] = useState<string | null>(null)

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
                            <img src={trash3} onClick={()=>setIsVisible(`dg-${drugGroup.id}`)}/>
                            <Modal 
                                id = {`dg-${drugGroup.id}`} 
                                isVisible={isVisible===`dg-${drugGroup.id}`} 
                                onClose={()=>setIsVisible(null)}
                                handler={()=>{deleteDrugGroupHendler(drugGroup.id)}}
                                message={`Вы хотите удалить группу ${drugGroup.dg_name}?`}
                            ></Modal>
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
import chevronRight from "../../../public/chevron-right.svg"
import trash3 from "../../../public/trash3.svg"
import { AddDrugForm } from "../../components/addDrugForm/addDrugForm"
import { ErrMessageCard } from '../messageCards/errMessageCard';

import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import {deleteDrug} from '../../redux/DrugManageSlice'

export const DrugManage = () =>{
    const dispatch = useAppDispatch()
    const drugList = useAppSelector((state)=>state.drugManage.drugs)

    const deleteDrugHendler = (id: string) =>{
        dispatch(deleteDrug(id))
    }

    return (
        <>
        <div className="w-75 mt-4 drugManage">
                <a className='link-dark' data-bs-toggle="collapse" href="#collapseAddDrug" role="button" aria-expanded="false" aria-controls="collapseAddDrug">
                    <div className="flex ai-center">
                        <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                        <h4>Добавить лекарственное средство</h4>
                    </div>
                </a>
                <div className="collapse mt-4" id="collapseAddDrug">
                    <AddDrugForm/>
                </div>
                
            </div>
            <hr/>

            <div className="w-100 mt-4 drugManage">
                <a className='link-dark' data-bs-toggle="collapse" href="#collapseGetDrug" role="button" aria-expanded="false" aria-controls="collapseGetDrug">
                    <div className="flex ai-center">
                        <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                        <h4>Список лекарственных средств</h4>
                        
                    </div>
                </a>
                <div className="collapse mt-4" id="collapseGetDrug">
                    {Array.isArray(drugList) ? ( drugList.length > 0 ? drugList.map((drug, index)=>
                    <>
                        <div className='flex jc-sb w-100 ps-3 pe-3' key={drug.id}>
                            <div>
                                <span className='me-3'>{index+1}.</span> 
                                <span>{drug.drug_name}</span>
                            </div>
                            <img src={trash3} onClick={()=>{deleteDrugHendler(drug.id)}}/>
                        </div>
                        <hr/>
                    </>
                    ): <ErrMessageCard message='Нет Добавленных лекарственных средств'/>)
                    :
                    <ErrMessageCard message="Не удалось получить список лекарственных средств. Пожалуйста, перезагрузите страницу или попробуйте позже"/>
                    }
                </div>
            </div>
        </>
    )
    
}
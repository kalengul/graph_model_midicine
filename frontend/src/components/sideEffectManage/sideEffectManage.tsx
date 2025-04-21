import { useEffect } from "react"
import {AddDrugGroupForm} from "../addSideEffectForm/addSideEffectForm"
import { SideEffectsTable } from '../sideEffectsTable/sideEffectsTable'

import chevronRight from "../../../public/chevron-right.svg"
import "./sideEffectManage.scss"

import { useDispatch, useSelector} from 'react-redux';
import {addValue, initStates} from '../../redux/SideEffectManageSlice'
import { RootState } from '../../redux/store';


export const SideEffectManage = () =>{
    const dispatch = useDispatch()
    useEffect(()=>{
        dispatch(initStates())
    },[])

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
        

       
    </>
    )
}
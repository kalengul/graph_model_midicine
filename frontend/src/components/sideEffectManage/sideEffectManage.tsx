import {AddDrugGroupForm} from "../addSideEffectForm/addSideEffectForm"
import { SideEffectsTable } from '../sideEffectsTable/sideEffectsTable'

import chevronRight from "../../../public/chevron-right.svg"
import "./sideEffectManage.scss"

export const SideEffectManage = () =>{
    return (
        <>
        <div className="w-75 mt-4 drugManage">
            <a className='link-dark' data-bs-toggle="collapse" href="#collapseAddDrugGroup" role="button" aria-expanded="false" aria-controls="collapseAddDrugGroup">
                <div className="flex ai-center">
                    <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                    <h4>Добавить побочный эффект</h4>
                </div>
            </a>
            <div className="collapse mt-4" id="collapseAddDrugGroup">
                <AddDrugGroupForm/>
            </div>
        </div>
        <hr/>

        <div className="w-100 mt-4 drugManage">
            <a className='link-dark' data-bs-toggle="collapse" href="#collapseGetDrug" role="button" aria-expanded="false" aria-controls="collapseGetDrug">
                <div className="flex ai-center">
                    <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                    <h4>Таблица побочных эффектов с рангами</h4>
                    
                </div>
            </a>
            <div className="collapse mt-4" id="collapseGetDrug">
              <SideEffectsTable/>
            </div>
        </div>
    </>
    )
}
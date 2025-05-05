import { Nav } from '../../components/nav/nav';
import { DrugManage } from '../../components/drugManage/drugManage'
import { DrugGroupManage } from "../../components/drugGroupManage/drugGroupManage"

import "./DataManagePage.scss"
import { SideEffectManage } from "../../components/sideEffectManage/sideEffectManage"

export const DataManagePage = ()=>{
    return(
        <div className="flex">
        <Nav></Nav>
        <main className="ms-2 p-3 w-100">
            <h1>Управление данными</h1>

            <nav className='mt-3'>
                <div className="nav nav-tabs" id="nav-tab" role="tablist">
                    <button className="nav-link active" id="nav-DrugGroup-tab" data-bs-toggle="tab" data-bs-target="#nav-DrugGroup" type="button" role="tab" aria-controls="nav-DrugGroup" aria-selected="true">Группы </button>
                    <button className="nav-link" id="nav-Drug-tab" data-bs-toggle="tab" data-bs-target="#nav-Drug" type="button" role="tab" aria-controls="nav-Drug" aria-selected="false">Лекарственные средства</button>
                    <button className="nav-link" id="nav-SideEffects-tab" data-bs-toggle="tab" data-bs-target="#nav-SideEffects" type="button" role="tab" aria-controls="nav-SideEffects" aria-selected="false">Побочные эффекты</button>
                </div>
            </nav>
            <div className="tab-content" id="nav-tabContent">
                <div className="tab-pane fade show active" id="nav-DrugGroup" role="tabpanel" aria-labelledby="nav-DrugGroup-tab">
                    <DrugGroupManage/>
                </div>
                <div className="tab-pane fade" id="nav-Drug" role="tabpanel" aria-labelledby="nav-Drug-tab">
                    <DrugManage/>
                </div>
                <div className="tab-pane fade" id="nav-SideEffects" role="tabpanel" aria-labelledby="nav-SideEffects-tab">
                    <SideEffectManage/>
                </div>
            </div>
        </main>
        </div>
    )
}
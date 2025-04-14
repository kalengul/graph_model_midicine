import { Route, Routes, Navigate } from "react-router-dom"

import { DrugManagePage } from "./pages/DrugManagea/DrugManageaPage"
import { SideEffectManage } from "./pages/SideEffectManage/SideEffectManagePage"

export const useRoutes = () =>{
    return(
        <Routes>
            {/* <Route path="/" element={<AddDataPage/>}/> */}
            <Route path="/dataManage" element={<DrugManagePage/>}/>
            <Route path="/drugManage" element={<DrugManagePage/>}/>
            <Route path="/sedeEffectsManage" element ={<SideEffectManage/>}/>
            <Route path="*" element={<Navigate to="/dataManage" replace />}/>                       
        </Routes>
    )
}
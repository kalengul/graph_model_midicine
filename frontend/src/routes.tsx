import { Route, Routes, Navigate } from "react-router-dom"

import { DrugManagePage } from "./pages/DrugManagea/DrugManageaPage"

export const useRoutes = () =>{
    return(
        <Routes>
            {/* <Route path="/" element={<AddDataPage/>}/> */}
            <Route path="/dataManage" element={<DrugManagePage/>}/>
            <Route path="/drugManage" element={<DrugManagePage/>}/>
            <Route path="*" element={<Navigate to="/dataManage" replace />}/>                       
        </Routes>
    )
}
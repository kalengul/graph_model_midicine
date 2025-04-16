import { Route, Routes, Navigate } from "react-router-dom"

import { DataManagePage } from "./pages/DataManagea/DataManagePage"

export const useRoutes = () =>{
    return(
        <Routes>
            {/* <Route path="/" element={<AddDataPage/>}/> */}
            <Route path="/dataManage" element={<DataManagePage/>}/>
            <Route path="/drugManage" element={<DataManagePage/>}/>
            <Route path="*" element={<Navigate to="/dataManage" replace />}/>                       
        </Routes>
    )
}
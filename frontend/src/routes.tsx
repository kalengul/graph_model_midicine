import { Route, Routes, Navigate } from "react-router-dom"

import { DataManagePage } from "./pages/DataManagea/DataManagePage"
import {ComputationMedScape} from "./pages/СomputationMedScape/ComputationMedScape"
import {ComputationFortran} from "./pages/СomputationFortran/ComputationFortran"

export const useRoutes = () =>{
    return(
        <Routes>
            {/* <Route path="/" element={<AddDataPage/>}/> */}
            <Route path="/dataManage" element={<DataManagePage/>}/>
            <Route path="/drugManage" element={<DataManagePage/>}/>
            <Route path="/computationMedScape" element={<ComputationMedScape/>}/>
            <Route path="/computationFortran" element={<ComputationFortran/>}/>
            <Route path="*" element={<Navigate to="/dataManage" replace />}/>                       
        </Routes>
    )
}
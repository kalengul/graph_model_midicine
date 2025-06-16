import { Route, Routes, Navigate } from "react-router-dom"

import {PrivateRoute} from "./routesPrivar"
import { DataManagePage } from "./pages/DataManagea/DataManagePage"
import {ComputationMedScape} from "./pages/СomputationMedScape/ComputationMedScape"
import {ComputationFortran} from "./pages/СomputationFortran/ComputationFortran"
import { SynonymsPage } from "./pages/SynonymsPage/SynonymsPage"
import { LoginPage } from "./pages/Login/LoginPage"

export const useRoutes = () =>{
    return(
        <Routes>
            
            <Route 
                path="/computationMedScape" 
                element={
                    <PrivateRoute>
                        <ComputationMedScape/>
                    </PrivateRoute>
                }
            />
            <Route path="/computationFortran" element={<ComputationFortran/>}/>
            <Route path="/login" element={<LoginPage/>}/>
            
            <Route 
                path="/dataManage" 
                element={<PrivateRoute>
                            <DataManagePage/>
                        </PrivateRoute>
               }
            />

            <Route 
                path="/synonyms"  
                element={
                    <PrivateRoute> 
                        <SynonymsPage/> 
                    </PrivateRoute>
                }
            />

            <Route path="*" element={<Navigate to="/computationMedScape" replace />}/>                       
        </Routes>
    )
}
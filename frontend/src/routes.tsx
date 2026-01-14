import { Route, Routes, Navigate } from "react-router-dom"

import {PrivateRoute} from "./routesPrivar"
import { DataManagePage } from "./pages/DataManagea/DataManagePage"
import {ComputationMedScape} from "./pages/СomputationMedScape/ComputationMedScape"
import {ComputationFortran} from "./pages/СomputationFortran/ComputationFortran"
import { ComputationBayes } from "./pages/ComputationBayes/ComputationBayes"
import { SynonymsPage } from "./pages/SynonymsPage/SynonymsPage"
import { LoginPage } from "./pages/Login/LoginPage"
import { GraphPage } from "./pages/GraphPage/GraphPage"
import {StatisticBayesPage} from "./pages/StatisticBayesPage/StatisticBayes"

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
            <Route path="/computationBayes" element={<ComputationBayes/>}/>
            <Route path="/graph/:id" element={<GraphPage/>}></Route>
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

            <Route 
                path="/statisticBayes"  
                element={
                    <PrivateRoute> 
                        <StatisticBayesPage/> 
                    </PrivateRoute>
                }
            />

            <Route path="*" element={<Navigate to="/computationFortran" replace />}/>                       
        </Routes>
    )
}
import React from "react"
import { Route, Routes, Navigate } from "react-router-dom"

import {InstructionsListPage} from './pages/InstructionsListPage/InstructionsListPage'
import {DocumentationsListPage} from "./pages/DocumentationsList/DocumentationsListPage"
import { GraphsListPage } from "./pages/GraphsListPage/GraphsListPage"
import { GraphDitailsPage } from "./pages/GraphDitailsPage/GraphDitailsPage"
import { GraphChakerPage } from "./pages/GraphChakerPage/GraphChakerPage"
import { AddGIDPage } from "./pages/AddGIDPage/AddGIDPage"

export const useRoutes = () =>{
    return(
        <Routes>
            <Route path="/instructions" exact element={<InstructionsListPage/>}/>
            <Route path="/documentations" exact element={<DocumentationsListPage/>}/>
            <Route path="/graphs" exact element={<GraphsListPage/>}/>
            <Route path="/graphs/:id"  exact element={<GraphDitailsPage/>}/>
            <Route path="/graphs/:id/checkresults/:schema_name" exact element={<GraphChakerPage/>}/>
            <Route path="/add/:id" exact element={<AddGIDPage/>}/>
            <Route path="*" element={<Navigate to="/graphs" replace />}/>             
        </Routes>
    )
}
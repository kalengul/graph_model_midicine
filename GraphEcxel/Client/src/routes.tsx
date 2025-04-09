import React from "react"
import { Route, Routes, Navigate } from "react-router-dom"

import  MarkForInstructions from "./pages/MarkForInstructions/MarkForInstructions";
import AddNewDrug from "./pages/AddNewDrug/AddNewDrug";
import ChandeDrug from "./pages/ChandeDrug/ChandeDrug"
import Instructions from "./pages/Instructions/Instructions"

export const useRoutes = () =>{
    return(
        <Routes>
            <Route path="/" exact element={<MarkForInstructions/>}/>
            <Route path="/instructionsfiles" exact element={<Instructions/>}/>
            <Route path="/add_drug" exact element={<AddNewDrug/>}/>
            <Route path="/drugs/:id"  exact element={<ChandeDrug/>}/>
            <Route path="*" element={<Navigate to="/" replace />}/>             
        </Routes>
    )
}
import React from "react"
import { useParams, useNavigate } from 'react-router-dom'

import { Nav } from "../../components/nav/nav"
import { ArrowLink } from "../../components/arrowLink/arrowLink"

import "./GraphChakerPage.css"

export const GraphChakerPage = () =>{
    const { id, schema_name } = useParams()
    const navigate = useNavigate();
    
    const retunClickHandler = ()=>{
        navigate(`/graphs/${id}`);
    }

    return(
        <div>
            <Nav></Nav>
            <ArrowLink className="flex jc-start" title={`графы | ${schema_name}`} onClick={retunClickHandler}/>
            <div className='flex jc-center'>
                <h1>Результаты проверки графа</h1>
            </div>
        </div>
    )
}
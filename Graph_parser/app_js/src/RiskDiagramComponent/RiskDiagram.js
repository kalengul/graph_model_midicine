import React, {useEffect, useRef} from "react";

import { d3RiskDiagram } from './d3.js';
import './RiskDiagram.css'


export const RiskDiagram = ()=>{
    const svgRef = useRef();

    const size = [200, 100]
    useEffect(() => {
        //отображение в виде сети
        d3RiskDiagram({riskParams: "Запрещено", svgRef: svgRef, size: size, radius: 100})

    }, [size])

    return (
        <div className='RiskDiagramСontainer' >
            <svg ref={svgRef} className='svgRiskDiagram'> </svg>
        </div>
    )
}
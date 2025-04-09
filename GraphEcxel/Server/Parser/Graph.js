import React, {useEffect, useRef} from "react";

import { d3Graph } from './d3.js';
import './Graph.css'

const testData = require("./testData/standart_graph.json")
//const testData = require("./testData/drug_0.json")


export const Graph = ()=>{
    const svgRef = useRef();

    const size = [500, 800]
    useEffect(() => {
        //отображение в виде сети
        d3Graph({graphData: testData, svgRef: svgRef, size: size})

    }, [testData, size])

    return (
        <div className='Graphcontainer' >
            <svg ref={svgRef} className='svgGraph'> </svg>
        </div>
    )
}
import React, {useEffect, useRef} from 'react';
import { useSelector} from 'react-redux';

import { DataParser } from './DataParser.js';

import { d3Graph } from './d3.js';


import './graphView.css'

export const GraphView =() =>{
    const svgRef = useRef();

    const graphSchem = useSelector(state=>state.graph)
    const selectedNodes = useSelector(state=>state.VerifyGraph.currentVerify)

    //Отображение графа
    useEffect(() => {
        const size = [800, 400] //Подумать няд адаптивностью размеров
        //Парсер данных 
        if(Object.keys(graphSchem.schema).length!=0){
            const dataParser = new DataParser(graphSchem.schema)
            const  graphData = dataParser.Parse(size)

            //отображение в виде сети
            d3Graph({graphData: graphData, svgRef: svgRef, selectedNodes: selectedNodes, size: size})
        }

    }, [graphSchem, selectedNodes]);
    
    return (
        <div className='Graphcontainer'>
            <svg ref={svgRef} className='svgGraph'> </svg>
        </div>
    )
}
import React, { useState, useEffect, useRef} from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addValue } from '../../redux/graphSlices';

import * as d3 from 'd3';

import { DataParser } from './DataParser.js';

import { d3Graph } from './d3.js';


import './graph.css'

export const GraphView =() =>{
    const svgRef = useRef();

    const [graphData, setGraphData] = useState({'nodes': [], 'links':[]})

    const graphSchem = useSelector(state=>state.graph)

    //Отображение графа
    useEffect(() => {
        //console.log(graphSchem.schema)
        //Парсер данных 
        if(Object.keys(graphSchem.schema).length!=0){
            const dataParser = new DataParser(graphSchem.schema)
            const  graphData = dataParser.Parse()

            //отображение в виде сети
            d3Graph({graphData: graphData, svgRef: svgRef})
        }

    }, [graphSchem]);
    
    return (
        <div className='Graphcontainer'>
            <svg ref={svgRef} className='svgGraph'> </svg>
        </div>
    )
}
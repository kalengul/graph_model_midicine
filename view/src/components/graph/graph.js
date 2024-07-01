import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from "react-force-graph-2d";
import * as d3 from "d3";

import {Data} from "./data.js"
import { DataParser } from './DataParser.js';

import './graph.css'

const myData2 = {
    "nodes": [ 
        { 
          "id": "id1",
          "name": "name1",
          "val": 1,
          "color": "#D9EDFF"
        },
        { 
          "id": "id2",
          "name": "name2",
          "val": 10,
          "color": "#B3CFE9" 
        },
        { 
            "id": "id3",
            "name": "name3",
            "val": 1,
            "color": "#D9EDFF" 
        },
    ],
    "links": [
        {
            "source": "id1",
            "target": "id2"
        },
        {
            "source": "id2",
            "target": "id3"
        },
    ]
}

const myData = Data

export const GraphView =() =>{
    const graphRef = useRef(null);
    const forceRef = useRef();

    useEffect(() => {
        const dataParser = new DataParser(Data)
        dataParser.Parse()



        // forceRef.current.d3Force("collide", d3.forceCollide(13));
        forceRef.current.d3Force("charge").strength(-90);
        forceRef.current.d3Force("link").distance(100);
        forceRef.current.d3Force("charge").distanceMax(250);
      }, []);


    //Отображение узлов
    const CanvasHandler = (node, ctx, globalScale) => {

        const label = node.id; //Подпись узла
        const fontSize = 9
        // const fontSize = node.isClusterNode //Если узел корневой, то размер 1 иначе другой
        //   ? 14 * (node.val / 1500)
        //   : 14 / (globalScale * 1.2);
        ctx.font = `${fontSize}px Sans-Serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = 'black'//node.isClusterNode ? "white" : "black"; //Если корень, то цвет белый иначе черный
        // if (node.isClusterNode) {
        //   // console.log();
        //    const lineHeight = fontSize * 1.2;
        //   const lines = label.split(",");
        //   let x = node.x;
        //   let y = node.y - lineHeight;
        //   for (let i = 0; i < lines.length; ++i) {
        //     ctx.fillText(lines[i], x, y);
        //     y += lineHeight;
        //   }
        // } else if (globalScale >= 3.5) {
          ctx.fillText(label, node.x, node.y + 1.5);
        //}
      }

    //Наведение на узел графа
    const HoverHandler = () =>{

    }
    
    
    return(
        <div className='Graphcontainer flex jc-center' ref={graphRef}>
            <ForceGraph2D
                ref={forceRef}
                graphData={Data} //Данные для отображения графа

                //Размеры окна (Посмотреть как сделать адаптивность в зависимости от ширены экрана)
                width = {1105} 
                height = {500}

                
                nodeRelSize={10} //Размер узлов

                nodeCanvasObjectMode={() => "after"} //Сначала отрсовка узла по умолчанию, затем применение nodeCanvasObject для его доработки
                nodeCanvasObject={CanvasHandler}

                onNodeHover = {HoverHandler} //Навередение на узел
            />
        </div>
    )
}
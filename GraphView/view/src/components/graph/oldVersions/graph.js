import React, { useState, useEffect, useRef, useLayoutEffect} from 'react';
import ForceGraph2D from "react-force-graph-2d";
import * as d3 from "d3";

import {Data} from "../graph_data.js"
import { DataParser } from '../DataParser.js';

import './graph.css'

export const GraphView =() =>{
    const forceRef = useRef();

    const [MyData, setMyData] = useState({'nodes': [], 'links':[]})
    const [collapsedClusters, setCollapsedClusters] = useState([]);
    const [initialCenter, setInitialCenter] = useState(true);

    useEffect(() => {
        const dataParser = new DataParser(Data)
        let newData = dataParser.Parse()

        setMyData({'nodes': newData.nodes, 'links': newData.links})

        let rootNodes = []
        newData.nodes.forEach(node=>{
            if (node.cluster.isRoot) rootNodes.push(node.id)
        })
        setCollapsedClusters(rootNodes)

        forceRef.current.d3Force("charge").strength(-10);
        forceRef.current.d3Force("link").distance(9);
        forceRef.current.d3Force("charge").distanceMax(10);
      }, []);


    //Отображение узлов
    const CanvasHandler = (node, ctx, globalScale) => {
        //console.log(node)
        const label = node.name; //Подпись узла
        const fontSize = node.cluster.isRoot ? 14 * (node.val / 250): 14 / (globalScale * 1.5);//9

        ctx.font = `${fontSize}px Sans-Serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = 'black'//node.isClusterNode ? "white" : "black"; //Если корень, то цвет белый иначе черный

        //отображение текста в зависимости от его типа (кластер или нет)
        if(node.cluster.isRoot){
              const lineHeight = fontSize * 1.1;
              const lines = label.split(" ");
              if(lines.length === 1){
                let x = node.x;
                let y = node.y; 
                ctx.fillText(lines[0], x, y);
              }else{
                let x = node.x;
                let y = node.y - lineHeight;
                for (let i = 0; i < lines.length; ++i) {
                        ctx.fillText(lines[i], x, y);
                        y += lineHeight;
                }
              }
              
        } else {
            ctx.fillText(label, node.x, node.y);
        }

    }

    //Отображение свзяей между узлами
    const linkCanvasHandler = (link, ctx, globalScale) => {

        if (link.highlighted) {
          ctx.strokeStyle = 'red'; // Цвет для выделенных связей
          ctx.lineWidth = 0.05; // Толщина для выделенных связей
        } else {
          ctx.strokeStyle = 'gray'; // Цвет для обычных связей
          ctx.lineWidth = 0.05; // Толщина для обычных связей
        }
   
        ctx.stroke();
    };

    //Наведение на узел графа (почему-то выделение связей работает только у амиодарона + при наведении кзлы прыгают)
    const HoverHandler = (node, hovering) => {
      if(MyData){
        let updatedMyData = { ...MyData };
        if(node){
          // Выделить связи узла
          updatedMyData.links.map((link) => {
            if (link.source.id === node.id || link.target.id === node.id) {
              link.highlighted = true;
              console.log(link)
            }
          });
        } else {
          // Снять выделение с связей
          updatedMyData.links.forEach((link) => {
              link.highlighted = false;
          });
        }
        setMyData({...updatedMyData});
      }
    }
    
    //Появление узлов меньших уровней при клике на родитела
    const NodeClickHandler = (node) => {
      //toggleClusterCollapse(node.id);
      // if (collapsedClusters.includes(node.id)) {
      //   forceRef.current.zoom(3.5, 400);
      //   forceRef.current.centerAt(node.x, node.y, 400);
      // }
    };
    
    
    
    return(
        <div className='Graphcontainer flex jc-center'>
            <ForceGraph2D
                ref={forceRef}
                graphData={MyData}

                width={(window.innerWidth <= 450) ? 350 : 1105 } //Поработать над адаптивностью
                height={500}

                enableAnimation={false}
                nodeRelSize={1}
                onEngineStop={() => {
                  if (initialCenter) {
                    forceRef.current.zoomToFit();
                  }
                  setInitialCenter(false);
                }}
                
                nodeCanvasObjectMode={() => "after"} //Сначала отрсовка узла по умолчанию, затем применение nodeCanvasObject для его доработки
                nodeCanvasObject={CanvasHandler}
                
                
                linkCanvasObjectMode={()=>"after"}
                linkCanvasObject={linkCanvasHandler}
                
                //enableNodeDrag={false} //Можно двигать узлы мышкой или нет

                //Видимость узлов
                // nodeVisibility={(node) => {
                //     if (!collapsedClusters.includes(node.id)) {
                //       return false;
                //     } else return true;
                // }}

                //Видимость связей
                // linkVisibility={(link) => {
                //     if (
                //       collapsedClusters.includes(link.source.id) && collapsedClusters.includes(link.target.id)
                //     ) {
                //       return true;
                //     } else return false;
                // }}

                // nNodeClick={NodeClickHandler}

                //onNodeHover = {HoverHandler} //Навередение на узел

                
            />
        </div>
    )
}
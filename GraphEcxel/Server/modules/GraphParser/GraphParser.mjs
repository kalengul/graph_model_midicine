import { v4 as uuid } from 'uuid';
import {NodeTypes} from "./models/NodeTypes.mjs"

export class GraphParser {
    nodeTypes = new NodeTypes();

    //Получение узла по Id
    GetNodeById = (graph, id)=>{
        return graph.nodes.find(node => node.id === id);
    }

    //Определение уровня узла
    AssignLevels=(graph)=>{
        const nodeLevels = {};
        const adjacencyList = {};
      
        // Инициализация уровней узлов и списка смежности
        graph.nodes.forEach(node => {
          nodeLevels[node.id] = 0; // Все узлы изначально имеют уровень 0
          adjacencyList[node.id] = [];
        });
      
        // Заполнение списка смежности
        graph.links.forEach(link => {
          const { source, target } = link;
          adjacencyList[target].push(source);
        });
      
        // Определение уровней узлов
        const queue = [];
        
        // Ищем узлы, которые ни разу не являются target
        graph.nodes.forEach(node => {
          const nodeId = node.id;
          if (adjacencyList[nodeId].length === 0) {
            nodeLevels[nodeId] = 0;
            console.log(node)
            queue.push(nodeId);
          }
        });

        console.log(queue)
        if(queue.length==0) return false
      
        // Выполнение обхода графа
        const startTime = Date.now();
        const timeout = 5000; // 5 секунд максимум

        while (queue.length > 0) {
          const current = queue.shift();
          const currentLevel = nodeLevels[current];
      
          graph.links.forEach(link => {
            if (link.source === current) {
              const target = link.target;
              if (nodeLevels[target] < currentLevel + 1) {
                nodeLevels[target] = currentLevel + 1;
                queue.push(target);
              }
            }
          });

          // Проверка на превышение времени выполнения
          if (Date.now() - startTime > timeout) {
            console.log('Цикл выполнялся слишком долго, принудительный выход');
            throw new Error('Цикл выполнялся слишком долго, принудительный выход');
            //return res.status(500).send('Операция прервана из-за таймаута');
          }
        }
      
        // Добавление уровня узлам в исходный граф
        //console.log(nodeLevels)
        graph.nodes.forEach(node => {
          node.level = nodeLevels[node.id];
        });

        //Определение максимального уровня
        graph.maxLevel = Math.max(...Object.values(nodeLevels))+1
        //console.log(maxLevel)

        console.log('Уровни определены')
    }

    //Удаление невидимых узлов и замена ID
    DeleteUnVisibleNotes=(graph)=>{
        //Удаляем узлы, которые не должны быть видны и меняем ID
        graph.nodes.forEach(node=>{
            if(!this.nodeTypes.ChekNodeVisible(node)){//Если узел не должен быть виден
                let idNode = node.id;
                //Удаляем узел из списка у копии графа
                graph.nodes = graph.nodes.filter(elem=>elem.id!==idNode)

                //Создаем новые связи
                let links_NodeSource = graph.links.filter(elem=>elem.source === idNode)
                let links_NodeTarget = graph.links.filter(elem=>elem.target === idNode)

                links_NodeSource.forEach(linkSourse => {
                    links_NodeTarget.forEach(linkTarget => {
                        graph.links.push({link: linkSourse.link, weight: linkSourse.weight, source: linkTarget.source, target: linkSourse.target})
                    })
                })

                //Удаляем старые связи
                graph.links = graph.links.filter(elem=>(elem.source !== idNode)&&(elem.target !== idNode))
            }
        })
    }

    //Замена ID и name
    ChangeId =(graph)=>{
      //console.log(graph.nodes)
      graph.nodes.map(node=>{
        if(!("name" in node)){
          //Исправояем ID на name и записываем уникальный ID
          const name = node.id
          node.name = name
          const newId = uuid()
          node.id = newId

          //Заменем sourse и target на новый id в links 
          graph.links.forEach(link => {
              if(link.source == node.name) link.source = node.id
              if(link.target == node.name) link.target = node.id

              link.id = uuid();
          })
        }
      })
    }

    //Объединение узлов в кластер (по ЛС или групппе)
    MergeClaster=(graph, clasterType)=>{

    }

    //Определение координат x, y для узлов
    GetPosition=(graph, window)=>{
      //console.log(window)
      //Определение высоты уровня
      let levelHeight = window.height/graph.maxLevel;
      //console.log(`levelHeight: ${levelHeight}`)

      //Определение y
      graph.nodes.forEach(node=>{
        node.y = levelHeight/2+((node.level+1)*window.yStep)+node.level*node.r  //(node.level+1)*levelHeight + node.r + window.yStep
        //console.log(node.level+" - "+ node.y)
      })

      //Определение x
      let lelesWidth_Map = new Map();
      for(let i =0; i< graph.maxLevel; i++){
        //Определяем узлы одного уровня
        let levelNodes = graph.nodes.filter(node=>node.level == i)
        //console.log(levelNodes.length)

        let levelWidth = window.width/levelNodes.length;
        //console.log(`levelWidth: ${levelWidth}`)

        lelesWidth_Map.set(i, levelWidth)
      }
      //console.log(lelesWidth_Map)

      graph.nodes.forEach(node=>{
        node.x = lelesWidth_Map.get(node.level)
        lelesWidth_Map.set(node.level, node.x+window.xStep+node.r);
        //node.x = (node.level+1)*levelHeight + window.yStep
      })

      //console.log(graph.nodes)
    }

    GetViewData=(graph, nodeView)=>{
      graph.nodes.forEach(node=>{
        node.r = nodeView.r
      })
    }

    GetLevelsInfo=(graph)=>{
      let NodesLevelCount = new Map();
      for(let i =0; i< graph.maxLevel; i++){
        //Определяем Количество узлов на одном уровне
        let levelNodes = graph.nodes.filter(node=>node.level == i)
        NodesLevelCount.set(i, levelNodes.length)
      }

      graph.levelsInfo = {levelNodesCount: {}}
      //console.log(NodesLevelCount)
      for (let elem of NodesLevelCount.keys()) {
        graph.levelsInfo.levelNodesCount[elem] = NodesLevelCount.get(elem);
      }
      
      //console.log(graph.levelsInfo)


    }

    Parse=(graph, windowData, nodeView)=>{
      
      if(!graph.isParse){
        console.log('Начало парсинга')
        //this.ChangeId(graph)
        
        try{
          this.AssignLevels(graph)

          this.GetViewData(graph, nodeView)
          this.GetLevelsInfo(graph)

          this.GetPosition(graph, windowData)


          graph.isParse = true
          return true
        } catch(err) {
          console.error(err)
          return false
        }
      }
      return false
    }

    constructor(){}
    
}
const { v4: uuidv4 } = require('uuid');

class GraphParser {
    nodeTypes = require('./models/NodeTypes')

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
            queue.push(nodeId);
          }
        });
      
        // Выполнение обхода графа
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
        }
      
        // Добавление уровня узлам в исходный граф
        //console.log(nodeLevels)
        graph.nodes.forEach(node => {
          node.level = nodeLevels[node.id];
        });

        //Определение максимального уровня
        graph.maxLevel = Math.max(...Object.values(nodeLevels))+1
        //console.log(maxLevel)
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

            //Исправояем ID на name и записываем уникальный ID
            node.name = node.id
            node.id = uuidv4();

            //Заменем sourse и target на новый id в links 
            graph.links.forEach(elem => {
                if(elem.source == node.name) elem.source = node.id
                if(elem.target == node.name) elem.target = node.id

                elem.id = uuidv4();
            })
        })
    }

    //Замена ID и name
    ChangeId =(graph)=>{
      graph.nodes.forEach(node=>{
            //Исправояем ID на name и записываем уникальный ID
            node.name = node.id
            node.id = uuidv4();

            //Заменем sourse и target на новый id в links 
            graph.links.forEach(elem => {
                if(elem.source == node.name) elem.source = node.id
                if(elem.target == node.name) elem.target = node.id

                elem.id = uuidv4();
            })
      })
    }

    //Объединение узлов в кластер (по ЛС или групппе)
    MergeClaster=(graph, clasterType)=>{

    }

    //Определение координат x, y для узлов
    GetPosition=(graph, window)=>{
      console.log(window)
      //Определение высоты уровня
      let levelHeight = window.height/graph.maxLevel;
      console.log(`levelHeight: ${levelHeight}`)

      //Определение y
      graph.nodes.forEach(node=>{
        node.y = (node.level+1)*levelHeight + window.yStep
      })

      //Определение x
      for(let i =0; i< graph.maxLevel; i++){
        //Определяем узлы одного уровня
        let levelNodes = graph.nodes.filter(node=>node.level == i)
        console.log(levelNodes.length)

        let levelWidth = window.width/levelNodes.length;
        console.log(`levelWidth: ${levelWidth}`)
        
      }

      //console.log(graph.nodes)
    }

    Parse=(graph, window)=>{
        //this.DeleteUnVisibleNotes(graph)
        this.ChangeId(graph)
        this.AssignLevels(graph)

        this.GetPosition(graph, window)
        
        //Функция привязки таблиц
    }

    constructor(){}
    
}

//let grapfData = require("./json/graph.json")
let grapfData = require("./json/standart_graph.json")
const graphParser = new GraphParser();
graphParser.Parse(grapfData, {width: 500, height: 700, xStep:10, yStep: 10});

//console.log(grapfData)
export class DataParser{
    constructor(data){
        this.inputData = data
    }

    Parse(){
        let outputData = {"nodes":[], "links": []}
        
        //Запись связей
        this.inputData.links.map((elem) => {
            let sourceNode = this._findNode('name', elem.source)
            let targetNode = this._findNode('name', elem.target)

            let newLink = {'source': sourceNode.id, 'target': targetNode.id, 'highlighted': false}
            outputData.links.push(newLink)
        })
        
        //Запись узлов
        this.inputData.nodes.map((elem)=>{
            let newNode = this._createNewNode(elem)
            outputData.nodes.push(newNode)
        })

        //Запись связей между кластерами
        


        console.log(outputData)

        return outputData
    }

    _findNode(type, param){
        switch (type) {
            case 'name':
                for(let i=0; i<this.inputData.nodes.length; i++){
                    let node = this.inputData.nodes[i];
                    if(node.name === param) return node
                }
                break;
            case 'parent':
                if(param == []) return null 
                else if (param.length === 1) {
                    for(let i=0; i<this.inputData.nodes.length; i++){
                        let node = this.inputData.nodes[i];
                        if(node.name === param[0]) return node
                    }
                }else {
                    //Ищем родителя на два уровня выше
                    let parent
                    for(let i=0; i<this.inputData.nodes.length; i++){
                        let node = this.inputData.nodes[i];
                        if(node.name === param[0]) parent = node
                    }
                    for(let i=0; i<this.inputData.nodes.length; i++){
                        let node = this.inputData.nodes[i];
                        if(node.name === parent.parent[0]) return node
                    }

                }

                break;
            default:
                break;
        }
    }

    _createNewNode(node){
        //Создание нового узла
        let newNode = {
            'id': node.id,
            'name': this._modifyString(node.name),
            'level': node.level,
            'cluster': this._findCluster(node),
            'val': this._getSizeNode(node),
            'color': this._getNodeColor(node),
        }
        
        
        return newNode
    }

    _getNodeColor(node){
        let nodeColor;
        let nodeType = this._findCluster(node)

        if(nodeType.isRoot) nodeColor = '#B3CFE9'
        else nodeColor = '#D9EDFF'

        return nodeColor
    }

    _getSizeNode(node){
        let nodeSize;
        let nodeType = this._findCluster(node)

        if(nodeType.isRoot && nodeType.id == null) nodeSize = 15
        else if(nodeType.isRoot && nodeType.id != null) nodeSize = 10
        else nodeSize = 4

        return nodeSize
    }

    _findCluster(node){
        if (node.level === 0) return {'id': null, 'isRoot': true}
        else if (node.level === 1) return {'id': node.id, 'isRoot': true}
        else if (node.level === 2) {
            let parentNodeId = this._findNode('parent', node.parent)
            return {'id': parentNodeId.id, 'isRoot': false}
        }
    }

    _modifyString(str){
        str = str.replaceAll('_', ' ')
        return str
    }
}
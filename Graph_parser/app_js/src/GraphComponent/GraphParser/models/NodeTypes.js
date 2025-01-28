class NodeTypes {
    constructor(){
        this.types = new Set()
        this.synonyms = require("./Synonyms")

        //Типы узлов (Которые отображаются на графе)
        const TYPES = ["drug", "active", "mechanism", "side_e", "recomendation", 
                       "group", "excreation", "prot_link", "metabol", "distribution", "banned"] 

        TYPES.forEach(elem => this.types.add(elem))
    }

    //Определение видимости узла
    ChekNodeVisible(node){
        //Если есть в словаре, заменяем
        if(this.synonyms.dictionary.has(node.label)) node.label = this.synonyms.dictionary.get(node.label)

        if(this.types.has(node.label)) return true
        return false
    }
}

module.exports = new NodeTypes()
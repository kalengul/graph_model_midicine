class Synonyms{
    constructor(){
        this.dictionary = new Map();

        this.dictionary.set("hormone", "mechanism")
        this.dictionary.set("prepare", "drug")
        this.dictionary.set("attention", "recomendation")


    }
}

module.exports = new Synonyms()
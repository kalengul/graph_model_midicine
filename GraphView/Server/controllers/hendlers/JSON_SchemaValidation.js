const Ajv = require('ajv');
const ajv = new Ajv();

class JSON_SchemaValidation{
    // Без учета тэгов instructions и humanInformation
    SCHEMA_MODEL = {
        type: "object",
        properties: {
            schema_name: { type: "string" },
            nodes: {
                type: "array",
                items: {
                    type: "object",
                    properties: {
                        id: { type: "string" },
                        name: { type: "string" },
                        parents: {
                            type: "array",
                            items: {type: "string"}

                        },
                        children: {
                            type: "array",
                            items: {type: "string"}
                        },
                        level: {type: "number"},
                        tag: {
                            type: "string",
                            enum: ["drug", "mechanism", "side-effect", "human"]
                        },
                        ratio: {type: "number"},
                        roots: {
                            type: "array",
                            items: {type: "string"}
                        }
                    },
                    required: ["id", "name", "parents", "children", "level", "tag", "ratio", "roots"],
                    additionalProperties: false
                }
            },
            links:{
                type: "array",
                items: {
                    type: "object",
                    properties: {
                        source: {type: "string"},
                        target: {type: "string"},
                        lable: {type: "string"},
                    }
                }
            }
        },
        required: ["schema_name", "nodes"], //обязательные свойcтва
        additionalProperties: false, //Без дополнительных свойств, неописанных в схеме
    };
    
    Validate(schema){
        const validate = ajv.compile(this.SCHEMA_MODEL);

        let valid = validate(schema);
        if(!valid) return {err: validate.errors}
        return {err: false} //Схема соответствует шаблону
    }
}

module.exports = new JSON_SchemaValidation()
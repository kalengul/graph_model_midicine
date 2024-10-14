export const Validator = (values) =>{
    const errors = {};

    if (!values.sourseNode) errors.sourseNode = "Пожалуйста, выберете узел источник";
    if (!values.targetNode) errors.targetNode = "Пожалуйста, выберете целевой узел";
    if(!values.statusLink) errors.statusLink = "Пожалуйста, определите корректность связи мужду узлами"

    return errors;
}
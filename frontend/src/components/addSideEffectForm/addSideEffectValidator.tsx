interface IAddSideEffectValidator{
    se_name?: string
}

interface IErrors{
    se_name?: string,
}



export const AddSideEffectValidator = (values: IAddSideEffectValidator) =>{
    const errors: IErrors={}
    if (!values.se_name) errors.se_name = "Пожалуйста введите название побочного эффекта";
    return errors
}
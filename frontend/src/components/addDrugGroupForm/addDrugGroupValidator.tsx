interface IAddDrugGroupValidator{
    dg_name?: string
}

interface IErrors{
    dg_name?: string,
}

export const AddDrugGroupValidator = (values: IAddDrugGroupValidator) =>{
    const errors: IErrors={}
    if (!values.dg_name) errors.dg_name = "Пожалуйста введите название группы лекарственных средств";
    return errors
}
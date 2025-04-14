interface IAddDrugValidator{
    drug_name?: string
}

interface IErrors{
    drug_name?: string,
}

export const AddDrugValidator = (values: IAddDrugValidator) =>{
    const errors: IErrors={}
    if (!values.drug_name) errors.drug_name = "Пожалуйста введите название лекарственного средсва";
    return errors
}
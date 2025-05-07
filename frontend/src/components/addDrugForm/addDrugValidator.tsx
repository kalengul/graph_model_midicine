import { ISendDrugData, ISendDrugDataError } from "../../redux/DrugManageSlice";

export const AddDrugValidator = (values: ISendDrugData) =>{
    const errors: ISendDrugDataError={}
    if (!values.drug_name) errors.drug_name = "Пожалуйста введите название лекарственного средства";
    return errors
}
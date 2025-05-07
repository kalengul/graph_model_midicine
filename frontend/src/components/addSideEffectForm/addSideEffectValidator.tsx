import { ISendSideEffectDataError, ISendSideEffectData } from "../../redux/SideEffectManageSlice";

export const AddSideEffectValidator = (values: ISendSideEffectData) =>{
    const errors: ISendSideEffectDataError={}
    if (!values.se_name) errors.se_name = "Пожалуйста введите название побочного эффекта";
    return errors
}
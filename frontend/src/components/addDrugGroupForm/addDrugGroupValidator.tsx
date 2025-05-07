import {ISendDrugGroupDataError, ISendDrugGroupData} from '../../redux/DrugGroupManageSlice'

export const AddDrugGroupValidator = (values: ISendDrugGroupData) =>{
    const errors: ISendDrugGroupDataError = {}
    if (!values.dg_name) errors.dg_name = "Пожалуйста введите название группы лекарственных средств";
    return errors
}
import { createSlice } from "@reduxjs/toolkit";

interface IPayload{
    se_id: string, //ключ сохраняемого объекта
    rank: number //значение для сохранения
}

interface IState {
    drug_name: string; // Указываем тип элементов массива
    side_effects: IPayload[];
    [key: string]: any; // Если state может содержать другие динамические поля
  }


const AddDrugSlice = createSlice({
    name: 'AddDrug',
    initialState: {
        drug_name: "",
        side_effects: [],
    } as IState,
    reducers: {}
})

export default AddDrugSlice.reducer; //Формирование reduser из набора методов из redusers
import { createSlice } from "@reduxjs/toolkit";

interface IPayload{
    id: string //ключ сохраняемого объекта
    drug_name: string //значение для сохранения
}

interface IState {
    drugs: IPayload[]; // Указываем тип элементов массива
    [key: string]: any; // Если state может содержать другие динамические поля
  }

const DrugManageSlice = createSlice({
    name: 'drugManage',
    initialState: {
        drugs: [],
    } as IState,
    reducers: {
        addValue(state, action){
            //console.log(action.payload)
            for(const key in state){
                if (key === action.payload.title) state[key] = action.payload.value
            }
        },

       initStates(state){
        state.drugs = []
       }
    }
})

export const {addValue,  initStates} = DrugManageSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default DrugManageSlice.reducer; //Формирование reduser из набора методов из redusers
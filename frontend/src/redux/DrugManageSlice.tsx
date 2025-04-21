import { createSlice } from "@reduxjs/toolkit";
import { IDrug } from "../interfaces/Interfaces";

interface IStateDrugs {
    drugs: IDrug[]; // Указываем тип элементов массива
    [key: string]: any; // Если state может содержать другие динамические поля
  }

const DrugManageSlice = createSlice({
    name: 'drugManage',
    initialState: {
        drugs: [],
    } as IStateDrugs,
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
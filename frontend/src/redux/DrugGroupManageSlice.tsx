import { createSlice } from "@reduxjs/toolkit";

interface IPayload{
    id: string //ключ сохраняемого объекта
    dg_name: string //значение для сохранения
}

interface IState {
    drugGroups: IPayload[]; // Указываем тип элементов массива
    updateList: boolean;
    [key: string]: any; // Если state может содержать другие динамические поля
  }

const DrugGroupManageSlice = createSlice({
    name: 'drugGroupManage',
    initialState: {
        drugGroups: [],
        updateList: false,
    } as IState,
    reducers: {
        addValue(state, action){
            //console.log(action.payload)
            //console.log(action.payload.title)
            
            for(const key in state){
                //console.log(key)
                if (key === action.payload.title) {
                    //console.log(action.payload.title)
                    state[key] = action.payload.value 
                }
            }
        },

       initStates(state){
        state.drugGroups = []
        state.updateList =  false
       }
    }
})

export const {addValue,  initStates} = DrugGroupManageSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default DrugGroupManageSlice.reducer; //Формирование reduser из набора методов из redusers
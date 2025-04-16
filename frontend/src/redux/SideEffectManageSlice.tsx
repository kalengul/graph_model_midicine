import { createSlice } from "@reduxjs/toolkit";

interface IPayload{
    id: string //ключ сохраняемого объекта
    se_name: string //значение для сохранения
}

interface IState {
    sideEffects: IPayload[]; // Указываем тип элементов массива
    updateList_se: boolean;
    [key: string]: any; // Если state может содержать другие динамические поля
  }

const SideEffectManageSlice = createSlice({
    name: 'sideEffectManage',
    initialState: {
        sideEffects: [],
        updateList_se: false,
    } as IState,
    reducers: {
        addValue(state, action){
            console.log(action.payload)
            console.log(action.payload.title)
            
            for(const key in state){
                console.log(key)
                if (key === action.payload.title) {
                    console.log(action.payload.title)
                    state[key] = action.payload.value 
                }
            }
        },

       initStates(state){
        state.sideEffects = []
        state.updateList_se =  false
       }
    }
})

export const {addValue,  initStates} = SideEffectManageSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default SideEffectManageSlice.reducer; //Формирование reduser из набора методов из redusers
import { createSlice } from "@reduxjs/toolkit";

interface IPayload{
    title: string //ключ сохраняемого объекта
    value: object //значение для сохранения
}

interface IState {
    links: IPayload[]; // Указываем тип элементов массива
    isActive: string;
    [key: string]: any; // Если state может содержать другие динамические поля
  }

const MenuSlice = createSlice({
    name: 'menu',
    initialState: {
        links: [],
        isActive: "",
    } as IState,
    reducers: {
        addValue(state, action){
            console.log(action.payload)
            for(const key in state){
                if (key === action.payload.title) state[key] = action.payload
            }
        },

       initStates(state){
        state.isActive = ""
        state.links = []
       }
    }
})

export const {addValue,  initStates} = MenuSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default MenuSlice.reducer; //Формирование reduser из набора методов из redusers
import {createSlice} from '@reduxjs/toolkit'

const graphSlice = createSlice({
    name: 'graph',
    initialState: {
        title: "",
        schema: {},
        checkNodesList: []
    },
    reducers: {
        addValue(state, action){ //action передает все, что нужно для работы
            //console.log(action.payload)
            state.title = action.payload.title;
            state.schema = action.payload.schema;
        },
    }
})

export const {addValue} = graphSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default graphSlice.reducer; //Формирование reduser из набора методов из redusers
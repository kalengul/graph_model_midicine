import {createSlice} from '@reduxjs/toolkit'

const VeriyGraphSlice = createSlice({
    name: 'VerifyGraph',
    initialState: {
        verifyData: [], //Массив проверенных связей между вершинами

        currentVerify: { //Текущие проверяемые вершины
            sourseNode: "",
            targetNode: "",
        }
    },
    reducers: {
        addVerifyNode(state, action){
            state.verifyData.push(action.payload);
        },

        addCurrentVerify(state, action){
            for(let key in state.currentVerify){
                if(key===action.payload.name){
                    state.currentVerify[key] = action.payload.value;
                }
            }
        },        

        changeVerifyNode(state, action){
            const verifiNodeId = action.payload.id
            state.verifyData.map((elem)=>{
                if(elem.id === verifiNodeId){
                    elem.statusLink = action.payload.newStatusLink;
                }
            })
        },

        deliteVerifyNode(state, action){
            const verifiNodeId = action.payload.id
            state.verifyData = state.verifyData.filter((elem) => elem.id !== verifiNodeId)
        },

        initialState(state, action){
            for(let key in state.currentVerify){
                state.currentVerify[key] = "";
            }
        }
    }
})

export const {addVerifyNode, changeVerifyNode, deliteVerifyNode, addCurrentVerify, initialState} = VeriyGraphSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default VeriyGraphSlice.reducer; //Формирование reduser из набора методов из redusers
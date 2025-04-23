import { createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import axios from "axios";

export interface IComputationElem {
  id: string,
  drug_name: string,
}

interface IResultMedscape{
  compatibility_medscape: string,
  description: string,
  drugs: string[]
}

interface IComputationState {
  computationList: IComputationElem[]
  resultMedscape: IResultMedscape
  [key: string]: any; // Если state может содержать другие динамические поля
}
interface sendFormMedScape{
  drugs: string[]
}

export const iteractionMedscape = createAsyncThunk('computationSlice/iteractionMedscape', async (data: IComputationElem[]) => {
  try {
      const sendData: sendFormMedScape = {drugs:[]}
      data.forEach(e=>sendData.drugs.push(e.id))

      const response = await axios.get('/api/iteraction_medscape/', {
        headers:{'Content-Type': 'application/json'},
        params: {drugs: sendData.drugs.join(", ")} 
      });
      if(response.data.result.status===200) return response.data.data;
  } catch (error) {
      console.error(`Ошибка при расчете совместимости medScape:\n`, error);
      return `Ошибка при добавлении совместимости medScape`; // Возвращаем пустой массив при ошибке
  }
});

const ComputationSlice = createSlice({
    name: 'computation',
    initialState: {
      computationList: [],
      resultMedscape: {
        compatibility_medscape: "",
        description: "",
        drugs: [],
      },
    } as IComputationState,
    reducers: {
      addValue(state, action){
        switch (action.payload.title) {
          case "computationList":
              if(!state.computationList.find(d=>d.id === action.payload.value.id)) 
                {
                  state.computationList.push(action.payload.value)
                }
            break;
        
          default:
            break;
        }
      },
      removeComputationElem (state, action){
        state.computationList = state.computationList.filter(c=>c.id!==action.payload)
      }
    },

    extraReducers: (builder) => {
        builder
        .addCase(iteractionMedscape.fulfilled, (state, action) => {
          state.resultMedscape = action.payload
        })
          
    },


})

export const {addValue, removeComputationElem} = ComputationSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default ComputationSlice.reducer; //Формирование reduser из набора методов из redusers
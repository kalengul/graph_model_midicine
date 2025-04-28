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

interface ISE{
  se_name: string,
  rank: number,
}

interface ISideEffectComputationFortran{
  сompatibility: string,
  effects: ISE[]
}

interface IDrugCombination{
  сompatibility: string
  drugs: string[]
}

interface IResultFortran{
  compatibility_medscape: string,
  сompatibility_fortran: string,
  rank_iteractions: number,
  side_effects: ISideEffectComputationFortran[],
  combinations: IDrugCombination[]
  description: string,
  drugs: string[]
}

interface IComputationState {
  computationList: IComputationElem[]
  resultMedscape: IResultMedscape
  resultFortran: IResultFortran
  isresultMedscape: boolean
  isresultFortran: boolean
  [key: string]: any; // Если state может содержать другие динамические поля
}
export interface sendForm{
  drugs: string[]
  humanData?: string
}

export interface IComputationFortran{
  drugs: IComputationElem[],
  humanData: string,
}

export const iteractionMedscape = createAsyncThunk('computationSlice/iteractionMedscape', async (data: IComputationElem[]) => {
  try {
    
      const sendData: sendForm = {drugs:[]}
      data.forEach(e=>sendData.drugs.push(e.id))

      const response = await axios.get('/api/iteraction_medscape/', {
        headers:{'Content-Type': 'application/json'},
        params: {drugs: `[${sendData.drugs.join(", ")}]`}
      });
      if(response.data.result.status===200) return response.data.data;
  } catch (error) {
      console.error(`Ошибка при расчете совместимости medScape:\n`, error);
      return `Ошибка при добавлении совместимости medScape`; // Возвращаем пустой массив при ошибке
  }
});

export const iteractionFortran = createAsyncThunk('computationSlice/iteractionFortran', async (data: IComputationFortran) => {
  try {
    
      const sendData: sendForm = {drugs:[]}
      data.drugs.forEach(e=>sendData.drugs.push(e.id))
      sendData.humanData = data.humanData

      const response = await axios.get('/api/polifarmakoterapiya-fortran/', {
        headers:{'Content-Type': 'application/json'},
        params: {drugs: `[${sendData.drugs.join(", ")}]`, humanData: {age: `[${sendData.humanData}]`}}
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
      isresultMedscape: false,
      resultFortran: {
        compatibility_medscape: "",
        сompatibility_fortran: "",
        rank_iteractions: 0,
        side_effects: [],
        combinations: [],
        description: "",
        drugs: [],
      },
      isresultFortran: false,
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
      },

      initResultMedscape(state){
        state.resultMedscape = {
          compatibility_medscape: "",
          description: "",
          drugs: [],
        }
        state.isresultMedscape = false
      },

      initResultFortran(state){
        state.isresultFortran = false
        state.resultFortran = {
          compatibility_medscape: "",
          сompatibility_fortran: "",
          rank_iteractions: 0,
          side_effects: [],
          combinations: [],
          description: "",
          drugs: [],
        }
      }
    },

    extraReducers: (builder) => {
        builder
        .addCase(iteractionMedscape.fulfilled, (state, action) => {
          state.isresultMedscape = true
          state.resultMedscape = action.payload
          // state.computationList = []
        })  
        .addCase(iteractionFortran.fulfilled, (state, action)=>{
          state.isresultFortran = true
          state.resultFortran = action.payload
          // state.computationList = []
        })  
    },
})

export const {addValue, removeComputationElem, initResultMedscape, initResultFortran} = ComputationSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default ComputationSlice.reducer; //Формирование reduser из набора методов из redusers
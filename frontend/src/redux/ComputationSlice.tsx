import { createSlice, PayloadAction, createAsyncThunk} from "@reduxjs/toolkit";
import axios from "axios";

export interface IComputationElem {
  id: string,
  drug_name: string,
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

export interface IResultFortran{
  // compatibility_medscape: string,
  сompatibility_fortran: string,
  rank_iteractions: number,
  side_effects: ISideEffectComputationFortran[],
  combinations: IDrugCombination[]
  // description: string,
  drugs: string[]
}

export interface IResultMedscape{
  compatibility_medscape: string,
  description: string,
  drugs: string[]
}

interface IComputationState {
  computationList: IComputationElem[]
  resultMedscape: IResultMedscape[]
  resultFortran: IResultFortran
  isresultMedscape: boolean
  isresultFortran: boolean
  [key: string]: any; // Если state может содержать другие динамические поля
}

const initStateFortran: IResultFortran = {
    // compatibility_medscape: "",
    сompatibility_fortran: "",
    rank_iteractions: 0,
    side_effects: [],
    combinations: [],
    // description: "",
    drugs: [],
}

// const initStateMedscape: IResultMedscape = {
//   compatibility_medscape: "",
//   description: "",
//   drugs: [],
// }

export interface sendForm{
  drugs: string[]
  humanData?: string
}

export interface IComputationFortran{
  drugs: IComputationElem[],
  humanData: string,
}

interface TrunkResult<T = any> {
  status: number | "err";
  data: T;
  message: string
}


export const iteractionMedscape = createAsyncThunk('computationSlice/iteractionMedscape', async (data: IComputationElem[]): Promise<TrunkResult<IResultMedscape[]>> => {
  try {
    
      const sendData: sendForm = {drugs:[]}
      data.forEach(e=>sendData.drugs.push(e.id))

      const response = await axios.get('/api/iteraction_medscape/', {
        headers:{'Content-Type': 'application/json'},
        params: {drugs: `[${sendData.drugs.join(", ")}]`}
      });
      if(response.data.result.status===200) return {status: 200, data: response.data.data, message: ""};
      return { status: "err", data: [], message:`Ошибка при добавлении совместимости medScape`}
  } catch (error) {
      console.error(`Ошибка при расчете совместимости medScape:\n`, error);
      return { status: "err", data: [], message:`Ошибка при добавлении совместимости medScape`}; // Возвращаем пустой массив при ошибке
  }
});

export const iteractionFortran = createAsyncThunk('computationSlice/iteractionFortran', async (data: IComputationFortran): Promise<TrunkResult<IResultFortran>> => {
  try {
    
      const sendData: sendForm = {drugs:[]}
      data.drugs.forEach(e=>sendData.drugs.push(e.id))
      sendData.humanData = data.humanData

      const response = await axios.get('/api/polifarmakoterapiya-fortran/', {
        headers:{'Content-Type': 'application/json'},
        params: {drugs: `[${sendData.drugs.join(", ")}]`, humanData: sendData.humanData}
      });
      if(response.data.result.status===200) return {status: 200, data: response.data.data, message: ""};
      return { status: "err", data: initStateFortran, message:`Ошибка при добавлении совместимости Fortran`}
  } catch (error) {
      console.error(`Ошибка при расчете совместимости Fortran:\n`, error);
      return { status: "err", data:initStateFortran, message:`Ошибка при добавлении совместимости Fortran`}; // Возвращаем пустой массив при ошибке
  }
});

const ComputationSlice = createSlice({
    name: 'computation',
    initialState: {
      computationList: [],
      resultMedscape: [], //initStateMedscape,
      isresultMedscape: false,
      resultFortran: initStateFortran,
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

      initStates(state){
        state.computationList = []
        state.resultMedscape = []//initStateMedscape
        state.isresultMedscape = false
        state.resultFortran = initStateFortran
        state.isresultFortran = false
      },

      initResultMedscape(state){
        state.resultMedscape = []//initStateMedscape
        state.isresultMedscape = false
      },

      initResultFortran(state){
        // if(state.computationList.length===0){
          state.resultFortran = initStateFortran
          state.isresultFortran = false
          state.computationList = []
        // }
      }
    },

    extraReducers: (builder) => {
        builder
        .addCase(iteractionMedscape.fulfilled, (state, action: PayloadAction<TrunkResult<IResultMedscape[]>>) => {
          if(action.payload.status === 200) 
          {
            state.isresultMedscape = true
            state.resultMedscape = action.payload.data
          }
          else if (action.payload.status === "err") state.isresultMedscape = false
        })  
        .addCase(iteractionFortran.fulfilled, (state, action: PayloadAction<TrunkResult<IResultFortran>>)=>{
          if( action.payload.status === 200) 
          {
            state.isresultFortran = true
            state.resultFortran =  action.payload.data
          }
          else if ( action.payload.status === "err") state.isresultFortran = false
        })  
    },
})

export const {addValue, removeComputationElem, initResultMedscape, initResultFortran, initStates} = ComputationSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default ComputationSlice.reducer; //Формирование reduser из набора методов из redusers
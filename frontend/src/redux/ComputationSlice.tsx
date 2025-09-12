import { createSlice, PayloadAction, createAsyncThunk} from "@reduxjs/toolkit";
import axios from "axios";

export interface IComputationElem {
  id: string,
  drug_name: string,
  dg_id: string,
}

export interface ISE{
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

export interface IResultBayes{
  сompatibility_bayes: string | undefined,
  rank_iteractions: number | undefined,
  side_effects: ISideEffectComputationFortran[],
  combinations: IDrugCombination[] | undefined
  drugs: string[]
}

export interface IResultMedscape{
  compatibility_medscape: string,
  description: string,
  drugs: string[]
}

export interface ICompareData{
  se_name: string,
  rankFortran: number | "-",
  rankBayes: number,
}

interface IComputationState {
  computationList: IComputationElem[]
  resultMedscape: IResultMedscape[]
  resultFortran: IResultFortran
  resultBayes: IResultBayes
  isresultMedscape: boolean
  isresultFortran: boolean
  isresultBayes: boolean
  compareSide_effects: ICompareData[]
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

const initStateBayes: IResultBayes = {
    сompatibility_bayes: undefined,
    rank_iteractions: undefined,
    side_effects: [],
    combinations: undefined,
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

export interface sendFormBayes{
  drugs: string[]
  humanData: IHumanData | undefined
}

export interface IComputationFortran{
  drugs: IComputationElem[],
  humanData: string,
}

interface IHumanData{
  age: string | undefined;
  gender: "man" | "woman" | undefined;
  cont_list: number[] | undefined;
}

export interface IComputationBayes{
  drugs: IComputationElem[],
  humanData: IHumanData | undefined,
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

export const iteractionBayes = createAsyncThunk('computationSlice/iteractionBayes', async (data: IComputationBayes): Promise<TrunkResult<IResultBayes>> => {
  try {
    
      const sendData: sendFormBayes = {drugs:[], humanData: undefined}
      data.drugs.forEach(e=>sendData.drugs.push(e.id))

      if(data.humanData){
        sendData.humanData = {age: undefined, gender: undefined, cont_list: []}
        sendData.humanData.age = data.humanData.age
        sendData.humanData.gender = data.humanData.gender
        data.humanData.cont_list?.forEach(e=>sendData.humanData?.cont_list?.push(e))
      }

      const response = await axios.post('/api/polifarmakoterapiya-bayes/', sendData, {
        headers:{'Content-Type': 'application/json'},
      });
      if(response.data.result.status===200) return {status: 200, data: response.data.data, message: ""};
      return { status: "err", data: initStateBayes, message:`Ошибка при добавлении совместимости Fortran`}
  } catch (error) {
      console.error(`Ошибка при расчете совместимости Fortran:\n`, error);
      return { status: "err", data:initStateBayes, message:`Ошибка при добавлении совместимости Fortran`}; // Возвращаем пустой массив при ошибке
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
      resultBayes: initStateBayes,
      isresultBayes: false,
      compareSide_effects:[],
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
      },

      initResultBayes(state){
        state.computationList = []
        state.isresultBayes = false
        state.resultBayes = initStateBayes
      },

      createCompareData(state){
        if(state.isresultBayes && state.isresultFortran){
          //заполняем побочки и ранги из байеса
          state.compareSide_effects = state.resultBayes.side_effects[0].effects.map((item: ISE)=>({
            se_name: item.se_name,
            rankFortran:  "-",
            rankBayes: item.rank,
          }))

          //Добавляем ранги из фортрана
          state.resultFortran.side_effects.forEach(group=>{
            group.effects.forEach(effect=>{
              const index = state.compareSide_effects.findIndex(item => item.se_name.trim().toLowerCase() === effect.se_name.trim().toLowerCase());
              if (index !== -1){
                state.compareSide_effects[index].rankFortran = effect.rank
              }else (console.log(effect.se_name.trim().toLowerCase()))
            })
          })
          
        } else state.compareSide_effects=[]
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
        .addCase(iteractionBayes.fulfilled, (state, action: PayloadAction<TrunkResult<IResultBayes>>)=>{
          if( action.payload.status === 200) 
          {
            state.isresultBayes = true
            state.resultBayes = action.payload.data
          }
          else if ( action.payload.status === "err") state.isresultBayes = false
        })
    },
})

export const {addValue, removeComputationElem, initResultMedscape, initResultFortran, initStates, initResultBayes, createCompareData} = ComputationSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default ComputationSlice.reducer; //Формирование reduser из набора методов из redusers
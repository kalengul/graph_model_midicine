import { createSlice, PayloadAction, createAsyncThunk} from "@reduxjs/toolkit";
import {IContElem} from "./ContraindicationsManageSlice"
import axios from "axios";

export interface IComputationElem {
  id: string,
  drug_name: string,
  nosology_id: string,
}

export interface IContraindicationsElem {
  id: string,
  cont_name: string,
} 

export interface ISE{
  se_name: string,
  rank: number,
}

export interface ISideEffectComputationFortran{
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

export interface ISEFromDrug{
  d_name: string,
  effects: ISE[]
}

export interface IResultBayes{
  сompatibility_bayes: string ,
  rank_iteractions: number | undefined,
  side_effects: ISideEffectComputationFortran[],
  SEFromDrug: ISEFromDrug[],
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

export interface ICompareDataFromDrug{
  d_name: string,
  effects: ICompareData[]
}

interface IComputationState {
  computationList: IComputationElem[]
  contList: IContElem[]
  resultMedscape: IResultMedscape[]
  resultFortran: IResultFortran
  resultBayes: IResultBayes
  isresultMedscape: boolean
  isresultFortran: boolean
  isresultBayes: boolean
  compareSide_effects: ICompareData[]
  compareSide_effects_fromDrug: ICompareDataFromDrug[],
  isLoadBayes: boolean
  isLoadFortran: boolean
  compareStart: boolean

  fetchBayesStatus: boolean | null
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
    сompatibility_bayes: "unknown",
    rank_iteractions: undefined,
    side_effects: [],
    SEFromDrug: [],
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
  cont_list: string[] | undefined;
}

export interface IComputationBayes{
  drugs: IComputationElem[],
  humanData: IHumanData ,
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

      // console.log(data.humanData)

      if(data.humanData){
        sendData.humanData = {age: undefined, gender: undefined, cont_list: undefined}
        sendData.humanData.age = data.humanData.age
        sendData.humanData.gender = data.humanData.gender
        if(data.humanData.cont_list) sendData.humanData.cont_list = []
        data.humanData.cont_list?.forEach(e=>sendData.humanData?.cont_list?.push(e))
      }

      // console.log(sendData)

      const response = await axios.post('/api/polifarmakoterapiya-bayes/', sendData, {
        headers:{'Content-Type': 'application/json'},
      })
      if(response.data.result.status===200) return {status: 200, data: response.data.data, message: ""};
      return { status: "err", data: initStateBayes, message:`Ошибка при добавлении совместимости Байеса`}
  } catch (err) {
      const error: any = err
      console.error(`Ошибка при расчете совместимости Байеса:\n`, error);
      return { status: error.response.data.data.result.status, data:initStateBayes, message: error.response.data}; // Возвращаем пустой массив при ошибке
  }
});

const ComputationSlice = createSlice({
    name: 'computation',
    initialState: {
      computationList: [],
      contList: [],
      resultMedscape: [], //initStateMedscape,
      isresultMedscape: false,
      resultFortran: initStateFortran,
      isresultFortran: false,
      resultBayes: initStateBayes,
      isresultBayes: false,
      compareSide_effects:[],
      compareSide_effects_fromDrug:[],
      isLoadBayes: false,
      isLoadFortran: false,
      compareStart: false,
      fetchBayesStatus: null
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
          case "contList":
            // console.log(action.payload.value)
            if(!state.contList.find(d=>d.cont_id === action.payload.value.cont_id))
            {
                state.contList.push(action.payload.value)
            }
            break;
          case "compareStart":
            state.compareStart = action.payload.value;
            break;
          default:
            break;
        }
      },
      removeComputationElem (state, action){
        state.computationList = state.computationList.filter(c=>c.id!==action.payload)
      },
      removeContElem(state, action){
        state.contList = state.contList.filter(c=>c.cont_id!==action.payload)
      },

      initStates(state){
        state.computationList = []
        state.contList = []
        state.resultMedscape = []//initStateMedscape
        state.isresultMedscape = false
        state.resultFortran = initStateFortran
        state.isresultFortran = false
        state.isLoadBayes = false
        state.isLoadFortran = false

        state.fetchBayesStatus = null
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
          state.contList = []
          state.isLoadFortran = false
        // }
      },

      initResultBayes(state){
        state.computationList = []
        state.contList = []
        state.isresultBayes = false
        state.resultBayes = initStateBayes
        state.isLoadBayes = false
        state.fetchBayesStatus = null
      },

      initLoad(state){
        state.isLoadBayes = false
        state.isLoadFortran = false
        state.fetchBayesStatus = null
      },

      createCompareData(state){
        if(state.isresultBayes && state.isresultFortran){
          //заполняем побочки и ранги из байеса
          state.compareSide_effects = state.resultBayes.side_effects[0].effects.map((item: ISE)=>({
            se_name: item.se_name,
            rankFortran:  "-",
            rankBayes: item.rank,
          }))

          //заполняем побочки для конкретных ЛС
          console.log(state.resultBayes.SEFromDrug)
          state.compareSide_effects_fromDrug = state.resultBayes.SEFromDrug.map((item: ISEFromDrug)=>({
            d_name: item.d_name,
            effects: item.effects.map((effect: ISE)=>({
              se_name: effect.se_name,
              rankFortran:  "-",
              rankBayes: effect.rank
            }))
          }))

          //Добавляем ранги из фортрана
          state.resultFortran.side_effects.forEach(group=>{
            group.effects.forEach(effect=>{
              let index = state.compareSide_effects.findIndex(item => item.se_name.trim().toLowerCase() === effect.se_name.trim().toLowerCase());
              // if(index == -1){
              //   state.compareSide_effects_fromDrug.map(se_fromDrug =>{
              //     index = se_fromDrug.effects.findIndex(item=>item.se_name.trim().toLowerCase() === effect.se_name.trim().toLowerCase())
              //     if(index !== -1) {
              //       se_fromDrug.effects[index].rankFortran = effect.rank
              //     }
              //   })
              // }else state.compareSide_effects[index].rankFortran = effect.rank

              
              
              if (index !== -1){
                state.compareSide_effects[index].rankFortran = effect.rank
              }
             //}//else (console.log(effect.se_name.trim().toLowerCase()))

              state.compareSide_effects_fromDrug.map(se_fromDrug =>{
                  index = se_fromDrug.effects.findIndex(item=>item.se_name.trim().toLowerCase() === effect.se_name.trim().toLowerCase())
                  if(index !== -1) {
                    se_fromDrug.effects[index].rankFortran = effect.rank
                }
              })
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
            state.isLoadFortran = true
          }
          else if ( action.payload.status === "err") {
            state.isresultFortran = false
            state.isLoadFortran = false
          }
        })
        .addCase(iteractionBayes.fulfilled, (state, action: PayloadAction<TrunkResult<IResultBayes>>)=>{
          if( action.payload.status === 200) 
          {
            //console.log(action.payload.data)
            state.isresultBayes = true
            state.resultBayes = action.payload.data
            state.isLoadBayes = true
            state.fetchBayesStatus = true

            if(state.resultBayes.сompatibility_bayes.trim()!=="banned"){
              //Сортируем результаты по убыванию ранга попбочки
              state.resultBayes.side_effects = state.resultBayes.side_effects.map(item => (
                {
                  сompatibility: item.сompatibility,
                  effects: item.effects.sort((a, b) => b.rank - a.rank)
                }
              ))
            }
          }
          else if ( action.payload.status === "err") {
            state.isresultBayes = false
            state.isLoadBayes = false
            state.fetchBayesStatus = false
          }
        })
        .addCase(iteractionBayes.rejected, (state)=>{
          console.log("Нет выбранного ЛС")
          state.fetchBayesStatus = false
        })
        
    },
})

export const {addValue, removeComputationElem, removeContElem, initResultMedscape, initResultFortran, initStates, initResultBayes, createCompareData, initLoad} = ComputationSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default ComputationSlice.reducer; //Формирование reduser из набора методов из redusers
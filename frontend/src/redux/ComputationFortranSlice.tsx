import { createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import axios, {AxiosError } from "axios";
// import {IContElem} from "./ContraindicationsManageSlice"
import {IResultFortran, ISEFromDrug} from "./Interfaces"

interface IIncreasedRiskDrugs{
  effect: string;
  drugs: string;
}

interface IComputationFortranState {
  resultFortran: IResultFortran
  isresultFortran: boolean
  isLoad: boolean
  isSend: boolean
  errMessage: string | undefined

  increasedRiskDrugs: IIncreasedRiskDrugs[]//ЛС из-за которых увеличился риск появления противопоказаний (для красного)
  [key: string]: any; // Если state может содержать другие динамические поля
}

const initStateFortran: IResultFortran = {
  compatibility_fortran: "unknown",
  rank_iteractions: undefined,
  side_effects: [],
  SEFromDrug: [],
  combinations: undefined,
  drugs: [],
  bannedPairs:[],
  bannedPairsCont:[],
}

interface IHumanData{
  age: number | undefined | null;
  gender: "man" | "woman" | undefined | null;
  cont_list: string[] | undefined | null;
}

export interface sendFormFortran{
  drugs: number[]
  humanData: IHumanData | undefined
  medCard?: File | null
}


interface IResult {
  status: number
  message: string
}

interface IResponseFortran {
  result: IResult,
  data: IResultFortran
}

interface IRejectFortran<T = any> {
  result: IResult;
  data: T;
}

export const iteractionFortran = createAsyncThunk<
  IResponseFortran, // Тип возвращаемого значения при успехе
  sendFormFortran, // Тип аргумента
  {
      rejectValue: IRejectFortran; // Тип rejectWithValue
  }
>('computationFortranSlice/iteractionFortran', async (data: sendFormFortran, { rejectWithValue }) => {
  try {
      const formData = new FormData();
      // Добавление данных
      formData.append('drugs', JSON.stringify(data.drugs));
      if (data.humanData) {
        formData.append('humanData', JSON.stringify(data.humanData));
      }
      if (data.medCard) {
        formData.append('medCard', data.medCard);
      }

      const response = await axios.post('/api/polifarmakoterapiya-fortran/', formData, {
        headers:{'Content-Type': 'multipart/form-data'},//'application/json'},
      })
      return response.data;
      
  } catch (err) {
    const error = err as AxiosError<IRejectFortran>;
    if (error.response) {
      return rejectWithValue(error.response.data);
    }
  }
});

interface IResponseAutoCompliteFortran{
  result: IResult,
  data: IHumanData
}

export const autoСompletionFortran = createAsyncThunk<
  IResponseAutoCompliteFortran, // Тип возвращаемого значения при успехе
  File, // Тип аргумента
  {
      rejectValue: IRejectFortran; // Тип rejectWithValue
  }
>('computationFortranSlice/autoCompliteFortran', async (data: File, { rejectWithValue }) => {
  try {
      const formData = new FormData();
      // Добавление данных
      formData.append('file', data);

      const response = await axios.post('/api/humandata_from_medcard/', formData, {
        headers:{'Content-Type': 'multipart/form-data'},//'application/json'},
      })
      return response.data;
      
  } catch (err) {
    const error = err as AxiosError<IRejectFortran>;
    if (error.response) {
      return rejectWithValue(error.response.data);
    }
  }
});

const ComputationFortranSlice = createSlice({
    name: 'computationBayes',
    initialState: {
      resultFortran: initStateFortran,
      isresultFortran: false,
      isLoad: true,
      isSend: false,
      errMessage: undefined,
      increasedRiskDrugs: [],
    } as IComputationFortranState,
    reducers: {
      initStates(state){
        state.isLoad = true
        state.isSend = false
        state.isresultFortran = false
        state.resultFortran = initStateFortran
        state.errMessage = undefined
        state.increasedRiskDrugs = []
      },
    },
    extraReducers: (builder) => {
      builder
      .addCase(iteractionFortran.fulfilled, (state, action)=>{
        switch (action.payload.result.status) {
          case 200:
            state.isLoad = true
            state.isSend = true
            state.isresultFortran = true
            state.errMessage = ""
            state.resultFortran = action.payload.data

            //Сортруем результаты по убыванию ранга
            if(action.payload.data.compatibility_fortran.trim()!=="banned") {
              //Сортируем результаты по убыванию ранга попбочки
              state.resultFortran.side_effects = state.resultFortran.side_effects.map(item => (
                {
                  compatibility: item.compatibility,
                  effects: item.effects.sort((a, b) => b.rank - a.rank)
                }
              ))
            }

            //Получаем increasedRiskDrugs для определения почему стало хуже если стало
            if(action.payload.data.compatibility_fortran.trim() === "incompatible" && action.payload.data.side_effects){
              //Получаем побочки с высоким риском появления
              const effects_incmpatible = action.payload.data.side_effects.find(e=>e.compatibility.trim()==="incompatible")
              //Определяем у каких ЛС они максимальные
              if(effects_incmpatible) {
                const drugs = action.payload.data.SEFromDrug
                effects_incmpatible.effects.map(e =>{
                  let MaxRank: number = -1; //Максимальное значение ранга
                  let drugName: string = ""//Название ЛС

                  drugs.map(drug => {
                    const drug_effect = GetDrugEffect(e.se_name, drug)
                    if(drug_effect && drug_effect.rank >= MaxRank) {
                      MaxRank = drug_effect.rank
                      drugName = drug.d_name
                    }
                  })

                  if(drugName!=="" &&  MaxRank!== -1){
                    state.increasedRiskDrugs.push({effect: e.se_name, drugs: drugName})
                  }
                })
              }
            }

            break;
          default:
            state.isLoad = true
            state.isSend = true
            state.isresultFortran = false
            state.resultBayes = initStateFortran
            break;
        }
      })
      .addCase(iteractionFortran.rejected, (state, action)=>{
        state.isLoad = true
        state.isSend = true
        state.isresultBayes = false
        state.resultBayes = initStateFortran

        state.errMessage = action.payload?.result.message
      })
      .addCase(iteractionFortran.pending, (state)=>{
        state.isLoad = false
        state.increasedRiskDrugs = []
        state.isSend = true
      })
    },
})

//Получем ранг по имени эффекта из ЛС
const GetDrugEffect = (effect_name: string, drug_effect: ISEFromDrug) =>{
  const effect = drug_effect.effects.find(e => e.se_name.trim().toUpperCase() === effect_name.trim().toUpperCase())
  return effect
}

export const { initStates} = ComputationFortranSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default ComputationFortranSlice.reducer; //Формирование reduser из набора методов из redusers
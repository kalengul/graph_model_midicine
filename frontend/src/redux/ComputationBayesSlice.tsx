import { createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import axios, {AxiosError } from "axios";
// import {IContElem} from "./ContraindicationsManageSlice"
import {IResultBayes} from "./Interfaces"

interface IComputationBayesState {
  resultBayes: IResultBayes
  isresultBayes: boolean
  isLoad: boolean
  errMessage: string | undefined
  isSend: boolean
  drugIds: string[]
  [key: string]: any; // Если state может содержать другие динамические поля
}

const initStateBayes: IResultBayes = {
    сompatibility_bayes: "unknown",
    rank_iteractions: undefined,
    side_effects: [],
    SEFromDrug: [],
    combinations: undefined,
    drugs: [],
}

interface IHumanData{
  age: string | undefined;
  gender: "man" | "woman" | undefined;
  cont_list: string[] | undefined;
}

export interface sendFormBayes{
  drugs: string[]
  humanData: IHumanData | undefined
}


interface IResult {
  status: number
  message: string
}

interface IResponseBayes {
  result: IResult,
  data: IResultBayes
}

interface IRejectBayes<T = any> {
  result: IResult;
  data: T;
}

export const iteractionBayes = createAsyncThunk<
  IResponseBayes, // Тип возвращаемого значения при успехе
  sendFormBayes, // Тип аргумента
  {
      rejectValue: IRejectBayes; // Тип rejectWithValue
  }
>('computationBayesSlice/iteractionBayes', async (data: sendFormBayes, { rejectWithValue }) => {
  try {
      const response = await axios.post('/api/polifarmakoterapiya-bayes/', data, {
        headers:{'Content-Type': 'application/json'},
      })
      return response.data;
      
  } catch (err) {
    const error = err as AxiosError<IRejectBayes>;
    if (error.response) {
      return rejectWithValue(error.response.data);
    }
  }
});

const ComputationBayesSlice = createSlice({
    name: 'computationBayes',
    initialState: {
      resultBayes: initStateBayes,
      isresultBayes: false,
      isLoad: true,
      isSend: false,
      errMessage: undefined
    } as IComputationBayesState,
    reducers: {
      initStates(state){
        state.isLoad = true
        state.isSend = false
        state.isresultBayes = false
        state.resultBayes = initStateBayes
        state.errMessage = undefined
      },
      addDrugIds(state, action){
        state.drugIds = action.payload
      }
    },
    extraReducers: (builder) => {
      builder
      .addCase(iteractionBayes.fulfilled, (state, action)=>{
        switch (action.payload.result.status) {
          case 200:
            state.isLoad = true
            state.isSend = true
            state.isresultBayes = true
            state.errMessage = ""
            state.resultBayes = action.payload.data

            //Сортруем результаты по убыванию ранга
            if(action.payload.data.сompatibility_bayes.trim()!=="banned") {
              //Сортируем результаты по убыванию ранга попбочки
              state.resultBayes.side_effects = state.resultBayes.side_effects.map(item => (
                {
                  сompatibility: item.сompatibility,
                  effects: item.effects.sort((a, b) => b.rank - a.rank)
                }
              ))
            }
            break;
          default:
            state.isLoad = true
            state.isSend = true
            state.isresultBayes = false
            state.resultBayes = initStateBayes
            break;
        }
      })
      .addCase(iteractionBayes.rejected, (state, action)=>{
        state.isLoad = true
        state.isSend = true
        state.isresultBayes = false
        state.resultBayes = initStateBayes

        state.errMessage = action.payload?.result.message
      })
      .addCase(iteractionBayes.pending, (state)=>{
            state.isLoad = false
            state.isSend = true
      })
    },
})

export const { initStates, addDrugIds} = ComputationBayesSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default ComputationBayesSlice.reducer; //Формирование reduser из набора методов из redusers
import { createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import axios, {AxiosError } from "axios";
// import {IContElem} from "./ContraindicationsManageSlice"
import {IResultFortran} from "./Interfaces"

interface IComputationFortranState {
  resultFortran: IResultFortran
  isresultFortran: boolean
  isLoad: boolean
  isSend: boolean
  errMessage: string | undefined
  [key: string]: any; // Если state может содержать другие динамические поля
}

const initStateFortran: IResultFortran = {
    сompatibility_fortran: "unknown",
    rank_iteractions: undefined,
    side_effects: [],
    SEFromDrug: [],
    combinations: undefined,
    drugs: [],
}

interface IHumanData{
  age: number | undefined;
  gender: "man" | "woman" | undefined;
  cont_list: string[] | undefined;
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
      
      // Добавляем простые данные
      formData.append('drugs', JSON.stringify(data.drugs));
      
      if (data.humanData) {
        formData.append('humanData', JSON.stringify(data.humanData));
      }
      
      // Добавляем файл, если он есть
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

const ComputationFortranSlice = createSlice({
    name: 'computationBayes',
    initialState: {
      resultFortran: initStateFortran,
      isresultFortran: false,
      isLoad: true,
      isSend: false,
      errMessage: undefined
    } as IComputationFortranState,
    reducers: {
      initStates(state){
        state.isLoad = true
        state.isSend = false
        state.isresultFortran = false
        state.resultFortran = initStateFortran
        state.errMessage = undefined
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
            if(action.payload.data.сompatibility_fortran.trim()!=="banned") {
              //Сортируем результаты по убыванию ранга попбочки
              state.resultFortran.side_effects = state.resultFortran.side_effects.map(item => (
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
        state.isSend = true
      })
    },
})

export const { initStates} = ComputationFortranSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default ComputationFortranSlice.reducer; //Формирование reduser из набора методов из redusers
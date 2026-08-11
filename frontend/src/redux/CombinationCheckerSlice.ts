import { createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import axios, {AxiosError } from "axios";

interface IResult {
  status: number
  message: string
}

interface IResponseReports {
  result: IResult,
  data: IResultReport[]
}


interface IResponseReport {
  result: IResult,
  data: IReport,
}

interface IReject<T = any> {
  result: IResult;
  data: T;
}

interface IReport{
    id: string;
    name: string;
    status: "running" | "completed" | "canceled" | "failed",
    started_at: null,
    finished_at: null,
    duration: null,
    max_combination_size: number,
    weight_version_name: string,
    total_iterations: number,
    completed_iterations: number,
    checked_combinations: number,
    found_combinations: number,
    pruned_combinations: number,
    progress: number,
    error_message: string,
}

interface IResultReport {
    id: string;
    name: string;
    status: "running" | "completed" | "canceled" | "failed";
    created_at: string;
    finished_at: null | string;
    progress: number;
    max_combination_size: number;
    weight_version_name: string;
}



export const fetchReportsList = createAsyncThunk<
  IResponseReports, // Тип возвращаемого значения при успехе
  void,// Тип аргумента
  {
      rejectValue: IReject; // Тип rejectWithValue
  }
>('CombinationCheckerSlice/fetchReportsList', async (_, { rejectWithValue }) => {
  try {
      const response = await axios.get('/api/reports/', {
        // 'Authorization': `Bearer ${localStorage.getItem('token')}`,//'application/json'},
        // 'Content-Type': 'application/json',
      })
      return response.data;
      
  } catch (err) {
    const error = err as AxiosError<IReject>;
    if (error.response) {
      return rejectWithValue(error.response.data);
    }
  }
});

interface ICreateReportFormData{
    name: string,
    max_combination_size: number,
    rank_name: "rang_base"
}
export const createReport = createAsyncThunk<
    IResponseReport, // Тип возвращаемого значения при успехе
    ICreateReportFormData, // Тип аргумента
    { rejectValue: IReject; } // Тип rejectWithValue
>('CombinationCheckerSlice/createReport', async (data: ICreateReportFormData, { rejectWithValue }) => {
    try {
        const response = await axios.post('/api/reports/', data, {
            // 'Authorization': `Bearer ${localStorage.getItem('token')}`,//'application/json'},
            // 'Content-Type': 'application/json',
        })
        return response.data;
        
    } catch (err) {
        const error = err as AxiosError<IReject>;
        if (error.response) {
        return rejectWithValue(error.response.data);
        }
    }
})

interface ICancelData{
    report_id: string
}
interface IResponseCancelRunReport {
  result: IResult,
  data: ICancelData, 
}
export const cancelRunReport = createAsyncThunk<
  IResponseCancelRunReport, // Тип возвращаемого значения при успехе
  void,// Тип аргумента
  {
      rejectValue: IReject; // Тип rejectWithValue
  }
>('CombinationCheckerSlice/cancelRunReport', async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/reports/running/cancel/', {
        // 'Authorization': `Bearer ${localStorage.getItem('token')}`,//'application/json'},
        // 'Content-Type': 'application/json',
      })
      return response.data;
      
    } catch (err) {
        const error = err as AxiosError<IReject>;
        if (error.response) {
        return rejectWithValue(error.response.data);
        }
    }
})

export const updateRunReport = createAsyncThunk<
  IResponseReport, // Тип возвращаемого значения при успехе
  void,// Тип аргумента
  {
      rejectValue: IReject; // Тип rejectWithValue
  }
>('CombinationCheckerSlice/updateRunReport', async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/api/reports/running/', {
        // 'Authorization': `Bearer ${localStorage.getItem('token')}`,//'application/json'},
        // 'Content-Type': 'application/json',
      })
      return response.data;
      
    } catch (err) {
        const error = err as AxiosError<IReject>;
        if (error.response) {
        return rejectWithValue(error.response.data);
        }
    }
})

interface ICombinationCheckerState{
    reports: IResultReport[];
    loadStatusReportsList: "unload" | "loading" | "load"
    newReport: IReport | undefined
    loadCreateNewReport: "unload" | "loading" | "load"
    errNewReport: string | undefined
    updateInfo: IReport | undefined
    [key: string]: any
}

const CombinationCheckerSlice = createSlice({
    name: 'combinationChecker',
    initialState: {
        reports: [],
        loadStatusReportsList: "unload",
        newReport: undefined,
        loadCreateNewReport: "unload",
        errNewReport: undefined,
        updateInfo: undefined,
    } as ICombinationCheckerState,

    reducers: {
        initStates(state){
            state.reports = [];
            state.loadStatusReportsList = "unload"
            state.newReport = undefined
            state.loadCreateNewReport = "unload"
            state.errNewReport = undefined
            state.updateInfo = undefined
        }
    },

    extraReducers: (builder) => {
    builder
        .addCase(fetchReportsList.pending, (state) => {
            state.loadStatusReportsList = 'loading';
        })
        .addCase(fetchReportsList.fulfilled, (state, action)=>{
            switch (action.payload.result.status) {
                case 200:
                    state.loadStatusReportsList = "load";
                    state.reports = action.payload.data;
                    console.log(action.payload.data.findIndex(e=>e.status === "running"))
                    if(action.payload.data.findIndex(e=>e.status === "running")>-1) state.loadCreateNewReport = "loading"
            }
        })
        .addCase(fetchReportsList.rejected, (state)=>{
            state.loadStatusReportsList = 'unload';
        })

        .addCase(createReport.fulfilled, (state, action)=>{
            switch (action.payload.result.status) {
                case 201:
                    state.newReport = action.payload.data
                    state.errNewReport = undefined
                    state.loadCreateNewReport = "loading"
                    state.updateInfo = undefined
            }
        })
        .addCase(createReport.rejected, (state)=>{
            state.errNewReport = "Ошибка при запуске оценки. Дождитесь окончания прошлых расчетов и попробуйте снова"
        })

        .addCase(cancelRunReport.fulfilled, (state, action)=>{
            state.loadCreateNewReport = "unload"
            
            //Обновляем статус
            const elemIndex = state.reports.findIndex(e => e.id == action.payload.data.report_id)
            if(elemIndex>-1){
                state.reports[elemIndex].status = "canceled"
            }
            state.updateInfo = undefined
        })

        .addCase(updateRunReport.fulfilled, (state, action)=>{
            state.updateInfo = action.payload.data
        })
    }
})

export const { initStates} = CombinationCheckerSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default CombinationCheckerSlice.reducer; //Формирование reduser из набора методов из redusers
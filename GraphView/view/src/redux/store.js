import {configureStore} from '@reduxjs/toolkit'
import graphSlice from './graphSlices'
import VeriyGraphSlice from './verifyGraphSlice'

//Конфигурируем Store
export default configureStore({
    reducer: {  //Подключение reduser из redusers.js
        graph: graphSlice,
        VerifyGraph: VeriyGraphSlice,
    }
}) 
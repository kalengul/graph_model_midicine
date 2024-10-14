import {configureStore} from '@reduxjs/toolkit'
import graphSlice from './graphSlices'

//Конфигурируем Store
export default configureStore({
    reducer: {  //Подключение reduser из redusers.js
        graph: graphSlice,
    }
}) 
import {combineReducers, configureStore} from '@reduxjs/toolkit'
import { persistStore, persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage";
import DrugsSlice from './DrugsSlice'

//Конфигурируем Store
// export default configureStore({
//     reducer: {  //Подключение reduser из redusers.js
//         drugs: DrugsSlice,
//     }
// })

const reducers = combineReducers({
    drugs: DrugsSlice,
});

const persistConfig = {
    key: "root",
    storage,
};

const persistedReducer = persistReducer(persistConfig, reducers);

const store = configureStore({
    reducer: persistedReducer,
    middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
        serializableCheck: {
            ignoredActions: ["persist/PERSIST", "persist/REHYDRATE"],
        },
    }),
});

const persistor = persistStore(store);
export { store, persistor };
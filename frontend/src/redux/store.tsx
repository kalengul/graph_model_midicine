import {combineReducers, configureStore} from '@reduxjs/toolkit'
import { persistStore, persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage";

import MenuSlice from './MenuSlice.tsx'
import AddDrugSlice from './AddDrugSlice.tsx'
import DrugManageSlice from './DrugManageSlice.tsx'

const reducers = combineReducers({
    menu: MenuSlice,
    addDrug: AddDrugSlice,
    drugManage: DrugManageSlice,
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
export type RootState = ReturnType<typeof store.getState>; // Типизированный RootState
export { store, persistor };
import {combineReducers, configureStore} from '@reduxjs/toolkit'
import { persistStore, persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage";

import MenuSlice from './MenuSlice.tsx'
import DrugManageSlice from './DrugManageSlice.tsx'
import DrugGroupManageSlice from './DrugGroupManageSlice.tsx'
import SideEffectManageSlice from './SideEffectManageSlice.tsx';

const reducers = combineReducers({
    menu: MenuSlice,
    drugManage: DrugManageSlice,
    drugGroupManage: DrugGroupManageSlice,
    sideEffectManage: SideEffectManageSlice,

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
export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>; // Типизированный RootState
export { store, persistor };
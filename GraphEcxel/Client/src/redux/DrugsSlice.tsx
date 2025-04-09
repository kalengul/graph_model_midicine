import { createSlice } from "@reduxjs/toolkit";

const DrugsSlice = createSlice({
    name: 'drugs',
    initialState: {
        drugs: [],
        chandedDrug: {},
        statusChanges: [],
        isAllSelected: false,
        isSelectedRows: [],
        drugsStatistic: {},
    },
    reducers: {
        addValue(state, action){ 
            state.drugs = action.payload; 

            if(action.payload.length!=0){
                
                state.drugsStatistic.drugsCount = action.payload.length
                state.drugsStatistic.end = action.payload.filter((drug)=>drug.status.toUpperCase() =='Завершен'.toUpperCase()).length
                state.drugsStatistic.inProcess = action.payload.filter((drug)=>drug.status.toUpperCase() =='В процессе'.toUpperCase()).length
                state.drugsStatistic.noInfo = action.payload.filter((drug)=>drug.status.toUpperCase() =='Недостаточно информации'.toUpperCase()).length
                state.drugsStatistic.onlyScan = action.payload.filter((drug)=>drug.status.toUpperCase() =='Есть только сканы инструкций'.toUpperCase()).length
                state.drugsStatistic.onlyInsertList = action.payload.filter((drug)=>drug.status.toUpperCase() =='Есть только листки вкладыши'.toUpperCase()).length
                state.drugsStatistic.noFarcodynamics = action.payload.filter((drug)=>drug.status.toUpperCase() =='Нет фаркакодинамики'.toUpperCase()).length
                state.drugsStatistic.noGRLS = action.payload.filter((drug)=>drug.status.toUpperCase() =='Нет в ГРЛС'.toUpperCase()).length
            }
        },

        addStatusChange(state, action){
            const drug_id: string = action.payload.drug_id;
            const newStatus: string = action.payload.newStatus;

            if(state.statusChanges==[]){state.statusChanges.push(action.payload)}
            else{
                let isChange: boolean = false;
                state.statusChanges.forEach(elem=>{
                    if(elem.drug_id==drug_id) 
                    {
                        elem.newStatus = newStatus
                        isChange = true;
                    }
                })

                if(!isChange)state.statusChanges.push(action.payload)
            }   

        },

        addChandedGrapg(state, action){
            state.chandedDrug = state.drugs.filter((drug)=>drug.id==action.payload)[0]
        },

        addIsAllSelected(state, action){ state.isAllSelected = action.payload; },

        addIsSelectedRows(state, action){
            let isSelected: boolean = false;

            if(state.isSelectedRows==[]) state.isSelectedRows.push(action.payload)

            state.isSelectedRows.forEach(elem=> {if(elem==action.payload) isSelected=true })
            if(!isSelected) state.isSelectedRows.push(action.payload)
        },

        deleteIsSelectedRows(state, action){
            state.isSelectedRows = state.isSelectedRows.filter((id)=>id!=action.payload)
        },

        deleteDrug(state, action){
            state.drugs = state.drugs.filter((drug) => drug.id !== action.payload)
        },

        initStatusChange(state){ state.statusChanges=[] },

        initSelected(state){ 
            state.isAllSelected=false 
            state.isSelectedRows = []
        }, 
    }
})

export const {addValue, addStatusChange,addIsAllSelected, addChandedGrapg, addIsSelectedRows, deleteDrug, deleteIsSelectedRows, initStatusChange, initSelected} = DrugsSlice.actions; //Actions создаются автоматически, нужно просто достать через деструкторизацию
export default DrugsSlice.reducer; //Формирование reduser из набора методов из redusers
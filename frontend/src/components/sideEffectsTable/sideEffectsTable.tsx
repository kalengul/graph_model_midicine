import { useEffect } from 'react'
import axios from 'axios'

import { useSelector, useDispatch} from 'react-redux';
import {addValue as addValueDrug, initStates as initSatesDrug} from '../../redux/DrugManageSlice'
import {addValue as addValueSE, initStates as initSatesSE} from '../../redux/SideEffectManageSlice'
import { RootState } from '../../redux/store';

import "./sideEffectsTable.scss"


export const SideEffectsTable = ()=>{
    const dispatch = useDispatch();
    const drugs = useSelector((state: RootState)=>state.drugManage.drugs)
    const sideEffects = useSelector((state: RootState)=>state.sideEffectManage.sideEffects)

    useEffect(()=>{
        console.log(sideEffects)
        if(!Array.isArray(drugs) || drugs.length==0){
            axios({ 
                method: "GET", 
                url: "/api/getDrug/", 
            }).then((res)=>{
                dispatch(addValueDrug({title: "drugs", value: res.data.data}))
            })
        }
        if (!Array.isArray(sideEffects) || sideEffects.length==0){
            axios({ 
                method: "GET", 
                url: "/api/getSideEffect/", 
            }).then((res)=>{
                //console.log( res.data.data)
                dispatch(addValueSE({title: "sideEffects", value: res.data.data}))
            })
        }
       
    }, [drugs, sideEffects, dispatch])
    
    return (
    <table className="SE-table table">
     <thead>
            <tr>
                <th scope="col">#</th>
                <th scope="col">ПЭ/ЛС</th>
                { Array.isArray(drugs) && drugs.map((drug)=>
                    <th scope="col" key={drug.id}>{drug.drug_name}</th>
                )}
                
            </tr>
        </thead>
        <tbody>
            {Array.isArray(sideEffects) && sideEffects.map((sideEffect, index)=>
                <tr key={sideEffect.id}>
                    <th scope="row">{index}</th>
                    <th>{sideEffect.se_name}</th>
                </tr>
            )}
            {/* <tr>
                <th scope="row">1</th>
                <td>Mark</td>
                <td>Otto</td>
                <td>@mdo</td>
            </tr>
            <tr>
                <th scope="row">2</th>
                <td>Jacob</td>
                <td>Thornton</td>
                <td>@fat</td>
            </tr>
            <tr>
                <th scope="row">3</th>
                <td colspan="2">Larry the Bird</td>
                <td>@twitter</td>
            </tr> */}
        </tbody>
    </table>
    )
}
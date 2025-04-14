import { useEffect } from 'react'
import axios from 'axios'

import { Nav } from "../../components/nav/nav"
import { AddDrugForm } from "../../components/addDrugForm/addDrugForm"

import { useDispatch, useSelector} from 'react-redux';
import {addValue, initStates} from '../../redux/DrugManageSlice'
import { RootState } from '../../redux/store';

import "./DrugManagePage.scss"
import chevronRight from "../../../public/chevron-right.svg"

export const DrugManagePage = ()=>{
    
    const dispatch = useDispatch()
    useEffect(()=>{
        dispatch(initStates())
        axios({ 
            method: "GET", 
            url: "/api/getDrug/", 
        }).then((res)=>{
            //console.log(res.data)
            dispatch(addValue({title: "drugs", value: res.data.data}))
        })
    }, [])

    const drugList = useSelector((state: RootState)=>state.drugManage.drugs)

    return(
        <div className="flex">
            <Nav></Nav>
            <main className="ms-2 p-3 w-100">
                <h1>Управление лекарственными средствами</h1>
                <div className="w-75 mt-4 drugManage">
                    <a className='link-dark' data-bs-toggle="collapse" href="#collapseAddDrug" role="button" aria-expanded="false" aria-controls="collapseAddDrug">
                        <div className="flex ai-center">
                            <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                            <h4>Добавить лекарственное средство</h4>
                        </div>
                    </a>
                    <div className="collapse mt-4" id="collapseAddDrug">
                        <AddDrugForm/>
                    </div>
                    
                </div>
                <hr/>

                <div className="w-75 mt-4 drugManage">
                    <a className='link-dark' data-bs-toggle="collapse" href="#collapseGetDrug" role="button" aria-expanded="false" aria-controls="collapseGetDrug">
                        <div className="flex ai-center">
                            <img className='me-2 chevron-icon' src={chevronRight} alt='chevronDown'/>
                            <h4>Список лекарственных средств</h4>
                            
                        </div>
                    </a>
                    <div className="collapse mt-4" id="collapseGetDrug">
                        {Array.isArray(drugList) ? drugList.map((drug)=>
                            <div>
                            </div>
                        )
                    :
                        <div>
                            <p>Не удалось получить список лекарственных средств</p>
                            <p>Пожалуйста, попробуйте позже</p>
                        </div>
                    }
                    </div>
                </div>
                

            </main>
        </div>
    )
}
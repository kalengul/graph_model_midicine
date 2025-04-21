import axios from 'axios'

import {Form} from 'react-final-form';
import { Input } from "../form/input/input"
import {AddDrugGroupValidator} from "./addDrugGroupValidator"
import "./addDrugGroupForm.scss"

import { useDispatch} from 'react-redux';
import {addValue} from '../../redux/DrugGroupManageSlice'
// import { RootState } from '../../redux/store';

interface ISendDrugData{
    dg_name: string,
}

export const AddDrugGroupForm = () =>{
    const dispatch = useDispatch()

    const SendHandler =async (values: ISendDrugData)=>{
        //window.alert(values.drug_name)

        const data = new FormData();
        data.append('dg_name', values.dg_name)

        try {
            await axios({ 
                method: "POST", 
                url: "/api/addDrugGroup/", 
                data,
                headers: { 'Content-Type': 'multipart/form-data'},
            }).then((res)=>{
              //console.log(res)
              alert(res.data.result.message)

              dispatch(addValue({title: "updateList", value: true}))
            })
            
          } catch (error) {
            console.log(error)
          }
    }

    const ScrollInto = () =>{
        const scrollElem = document.querySelector('[data-err=true]')
        if(scrollElem) {
            scrollElem.scrollIntoView({ 
                behavior: 'smooth',  // Добавляем плавную прокрутку
                block: 'nearest'
            });
        }
      }

    return (
        <div>
            <Form 
                onSubmit={SendHandler}
                validate={(values)=>AddDrugGroupValidator(values)}
            >
            {({ handleSubmit, submitting}) => (
            <form onSubmit={handleSubmit}>
                <Input label="Название группы лекарственных средств" 
                    name = "dg_name"
                    id = "dg_name"
                    type = "text"
                    placeholder = "Введите название группы лекарственных средств"
                ></Input>

                <button className='btn send-btn' onClick={ScrollInto} disabled={submitting} >Добавить</button>
            </form>
            )}
            </Form>
        </div>
    )
}
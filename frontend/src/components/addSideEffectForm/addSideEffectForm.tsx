import axios from 'axios'

import {Form} from 'react-final-form';
import { Input } from "../form/input/input"
import {AddSideEffectValidator} from "./addSideEffectValidator"
import "./addSideEffectForm.scss"

import { useDispatch} from 'react-redux';
import {addValue, ISendSideEffectData} from '../../redux/SideEffectManageSlice'




export const AddDrugGroupForm = () =>{
    const dispatch = useDispatch()

    const SendHandler =async (values: ISendSideEffectData)=>{
        //window.alert(values.drug_name)

        const data = new FormData();
        data.append('se_name', values.se_name)

        try {
            await axios({ 
                method: "POST", 
                url: "/api/addSideEffect/", 
                data,
                headers: { 'Content-Type': 'multipart/form-data'},
            }).then((res)=>{
              //console.log(res)
              alert(res.data.result.message)

              dispatch(addValue({title: "updateList_se", value: true}))
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
                validate={(values)=>AddSideEffectValidator(values)}
            >
            {({ handleSubmit, submitting}) => (
            <form onSubmit={handleSubmit}>
                <Input label="Название побочного эффекта" 
                    name = "se_name"
                    id = "se_name"
                    type = "text"
                    placeholder = "Введите название побочного эффекта"
                ></Input>

                <button className='btn send-btn' onClick={ScrollInto} disabled={submitting} >Добавить</button>
            </form>
            )}
            </Form>
        </div>
    )
}

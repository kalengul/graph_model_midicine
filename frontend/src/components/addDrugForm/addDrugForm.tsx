import axios from 'axios'

import {Form} from 'react-final-form';
import { Input } from "../form/input/input"
import {AddDrugValidator} from "./addDrugValidator"
import "./addDrugForm.scss"

interface ISendDrugData{
    drug_name: string,
}

export const AddDrugForm = () =>{

    const SendHandler =async (values: ISendDrugData)=>{
        //window.alert(values.drug_name)

        const data = new FormData();
        data.append('drug_name', values.drug_name)

        try {
            await axios({ 
                method: "POST", 
                url: "/api/addDrug/", 
                data,
                headers: { 'Content-Type': 'multipart/form-data'},
            }).then((res)=>{
              //console.log(res)
              alert(res.data.message)
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
                validate={(values)=>AddDrugValidator(values)}
            >
            {({ handleSubmit, submitting}) => (
            <form onSubmit={handleSubmit}>
                <Input label="Название лекарственного средства" 
                    name = "drug_name"
                    id = "drug_name"
                    type = "text"
                    placeholder = "Введите название лекарственного средства"
                ></Input>

                <button className='btn send-btn' onClick={ScrollInto} disabled={submitting} >Добавить</button>
            </form>
            )}
            </Form>
        </div>
    )
}
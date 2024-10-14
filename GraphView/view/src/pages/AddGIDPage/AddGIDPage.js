import React, { useEffect, useState} from "react"
import {useNavigate, useParams} from 'react-router-dom'
import { Form} from 'react-final-form';
import {Field } from 'react-final-form';
import axios from 'axios'

import { GetData } from "./getPageData"
import { Validator } from "./dataValidator";

import { Nav } from "../../components/nav/nav"
import { Button } from '../../components/button/button'; 
import { ArrowLink } from "../../components/arrowLink/arrowLink"

import "./AddGIDPage.css"

export const AddGIDPage = () =>{
    const [pageData, setPageData] = useState()
    const [file, setFile] = useState(null);
    const { id } = useParams()
    const navigate = useNavigate();
 
    
    const retunClickHandler = ()=>{
        navigate(`/graphs`);
    }

    //Прокрутка к полю с ошибкой заполнения
    const ScrollInto = () =>{
        let scrollElem = document.querySelector('[data-err=true]')
        if(scrollElem) {
            document.querySelector('[data-err=true]').scrollIntoView();
        }
    }

    //Добавление данных на сервер
    const AddHandler = async (values) =>{
        const data = new FormData();

        data.append('typeData', file ? "file" : "textData");  // Добавляем JSON-строку как отдельное поле

        if(file){
            data.append('file', file);
        }else{
            data.append('data', values.schem_text);
            data.append('title', values.schem_name);
        }

        try {
            const response = await axios({ 
                method: "POST", 
                url: "http://localhost:7000/api/graphs/addnew", 
                data,
                headers: { 'Content-Type': 'multipart/form-data'},
            }).then((value)=>alert(value.data))
            
        } catch (error) {}
        
        setFile(null)
        navigate(`/graphs`);
    }


    // Обработчик изменения файла
    const fileChangeHandler = (e) => {
        setFile(e.target.files[0]); // Сохраняем выбранный файл в состояние
    };

    // Обработчик удаления файла
    const fileRemoveHandler = () => {
        setFile(null); // Удаляем файл из состояния
        document.getElementById("schem_file").value = ""; // Очищаем input
    };


    useEffect(()=>{
        const data = GetData(id)
        if(!data) navigate(`/graphs`)
        setPageData(data)
    }, [id])

    return (
        <div>
            <Nav></Nav>
            {pageData ? (
            <>
                <ArrowLink className="flex jc-start" title={pageData.returnLinkTitle} onClick={(e)=>retunClickHandler()}/>

                <div className='flex jc-center'>
                    <h1>{pageData.title}</h1>
                </div>

                <Form onSubmit={AddHandler} validate={(values)=>Validator(values, file)}>
                    {({ handleSubmit, submitting}) => (
                        <form onSubmit={handleSubmit}>
                            <Field name='schem_name' type='text' placeholder='Введиде название схемы графа'>
                            {({ input, meta, ...rest }) => (
                                <div data-err={meta.error && meta.touched}>
                                    <lable>Название</lable>
                                    <input {...input} {...rest}  className={(meta.error && meta.touched) ? 'errBorder' : ''}/>

                                    {meta.error && meta.touched && <span className='err'>{meta.error}</span>}
                                </div>
                            )}
                            </Field>

                            <div>
                                <Field name='schem_text' placeholder='Введиде структуру схемы в формате json'>
                                {({ input, meta, ...rest }) => (
                                    <div data-err={meta.error && meta.touched}>
                                        <lable>Структура графа</lable>
                                        <textarea {...input} {...rest} className={(meta.error && meta.touched) ? 'errBorder' : ''}/>
                                        {meta.error && meta.touched && <span className='err'>{meta.error}</span>}
                                    </div>
                                )}
                                </Field>

                               
                                    <div className="flex align-center">
                                        <input  name='schem_file' id = "schem_file" type="file" accept=".json" 
                                            onChange={fileChangeHandler}
                                        />
                                        {file && (
                                            <Button view="delete" onClick={fileRemoveHandler}/>
                                        )}
                                    </div>

                            </div>
                            
                            <Button lable = "Сохранить" view="fill" onClick={ScrollInto}/>
                            
                        </form>
                    )}
                </Form>
            </>
            ) : (
                <p>Загрузка...</p>
            )}
        </div>
    )
}
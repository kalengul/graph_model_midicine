import React, {useEffect, useState} from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Form} from 'react-final-form';
import {Field } from 'react-final-form';
import axios from 'axios';
import { useDispatch , useSelector} from 'react-redux';
import { addValue } from '../../redux/graphSlices';

import { Validator } from "./dataValidator";

//Components
import { Nav } from "../../components/nav/nav";
import { GraphView } from '../../components/graph/graph'
import { ArrowLink } from "../../components/arrowLink/arrowLink"
import { Button } from '../../components/button/button';

import "./GraphDitailsPage.css"

export const GraphDitailsPage = () =>{
    const navigate = useNavigate();
    const { id } = useParams()

    const [graphDitails, setGraphDitails] = useState({})
    const [checkNodes, setCheckNodes] = useState({ sourseNode: null, targetNode: null })
    const dispatch = useDispatch()

    useEffect(()=>{
        try {
            const response = axios({ 
                method: "GET", 
                url: `http://localhost:7000/api/graphs/${id}`, 
            }).then((res)=>{
                setGraphDitails(res.data.Data) //Доваление в useState
                
                //Сохранение схемы в redux
                dispatch(addValue({
                    title: res.data.Data.title,
                    schema: res.data.Data.schema, // Предполагается, что у вас есть поле 'schema' в данных
                }));
            })

        } catch (e) {}
    }, [])

    const graphSchem = useSelector(state=>state.graph)

    const retunClickHandler = ()=>{ navigate(`/graphs`) }
    const nextPageHandler = () => { navigate(`/graphs/${id}/checkresults/${graphDitails.title}`) }

    const ScrollInto = () =>{
        let scrollElem = document.querySelector('[data-err=true]')
        if(scrollElem) {
            document.querySelector('[data-err=true]').scrollIntoView();
        }
    }

    // const ChangeNodeHandler = (e) =>{
    //     setCheckNodes({...checkNodes, [e.target.name]:e.target.value})
    // }
    // console.log(checkNodes)

    const addNewRecordHandler = (values) =>{
        console.log(values)
    }



    return (
        <div>
            <Nav></Nav>
            <ArrowLink className="flex jc-start" title={"графы"} onClick={(e)=>retunClickHandler()}/>
            <div className='flex jc-center'>
                <h1>Граф - {graphDitails.title}</h1>
            </div>

            <div className='flex jc-sb detail-main'>
                <GraphView/>
                <div className='chack-container'>
                    <Form onSubmit={addNewRecordHandler} validate={(values)=>Validator(values)}>
                        {({ handleSubmit, submitting}) => (
                            <form onSubmit={handleSubmit}>
                                <lable>Узлы:</lable>
                                <div className='nodeChoice-block'>
                                    <Field name='sourseNode' nodes={graphSchem.schema.nodes} placeholder = "Выберете узел источник"> 
                                        {({ input, meta, ...props }) => (
                                            <div data-err={meta.error && meta.touched}>
                                                <select {...input} {...props} className={(meta.error && meta.touched) ? 'errBorder' : ''}>
                                                    <option value = {""}>{props.placeholder}</option>
                                                    { (props.nodes) ? (
                                                        props.nodes.map((elem) =>
                                                            <option value = {elem.id} key={elem.id}>{elem.name}</option>
                                                        )
                                                    ) : (<option value = {""}>Загрузка...</option>)}
                                                </select>
                                                {meta.error && meta.touched && <span className='err'>{meta.error}</span>}
                                            </div>
                                        )}
                                    </Field>

                                    <Field name='targetNode' nodes={graphSchem.schema.nodes} placeholder = "Выберете целевой узел">
                                        {({ input, meta, ...props }) => (
                                            <div data-err={meta.error && meta.touched}>
                                                <select {...input} {...props} className={(meta.error && meta.touched) ? 'errBorder' : ''}>
                                                    <option value = {""}>{props.placeholder}</option>
                                                    { (props.nodes) ? (
                                                        props.nodes.map((elem) =>
                                                            <option value = {elem.id} key={elem.id}>{elem.name}</option>
                                                        )
                                                    ) : (<option value = {""}>Загрузка...</option>)}
                                                </select>
                                                {meta.error && meta.touched && <span className='err'>{meta.error}</span>}
                                            </div>
                                        )}
                                    </Field>
                                </div>
                                
                                
                                <lable>Состояние связи:</lable>
                                <div>
                                    <Field name = "statusLink" type='radio' value="1" lable = "Связь есть и она корректна">
                                        {({ input, meta, ...props }) => (
                                                <div className='flex radio-block' >
                                                    <input {...input}/>
                                                    <label>{props.lable}</label>
                                                </div>
                                        )}
                                    </Field>

                                    <Field name = "statusLink" type='radio' value="-1" lable = "Связь есть, но она некорректна">
                                        {({ input, meta, ...props }) => (
                                                <div className='flex radio-block'>
                                                    <input {...input}/>
                                                    <label>{props.lable}</label>
                                                </div>
                                        )}
                                    </Field>

                                    <Field name = "statusLink" type='radio' value="0" lable = "Связь отсутсвует, но она должна быть">
                                        {({ input, meta, ...props }) => (
                                                <div data-err={meta.error && meta.touched}>
                                                    <div className='flex radio-block' >
                                                        <input {...input}/>
                                                        <label>{props.lable}</label>
                                                    </div>
                                                    {meta.error && meta.touched && <span className='err'>{meta.error}</span>}
                                                </div>
                                        )}
                                    </Field>
                                </div>
                               
                                <div className='flex btn-block'>
                                    <Button type = "submit" view="fill" lable="Добавить" onClick={ScrollInto}></Button>
                                    <Button view="unfill" lable="Далее" onClick={nextPageHandler}></Button>
                                </div>
                            </form>
                        )}
                    </Form>
                </div>
            </div>
        </div>
    )
}
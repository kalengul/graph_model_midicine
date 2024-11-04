import React, {useEffect, useState} from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Form} from 'react-final-form';
import {Field } from 'react-final-form';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'
import { useDispatch , useSelector} from 'react-redux';
import { addValue } from '../../redux/graphSlices';
import { addVerifyNode, addCurrentVerify, initialState} from '../../redux/verifyGraphSlice';

import { Validator } from "./dataValidator";
import {numStatusLink} from "../../functions/numerators"

//Components
import { Nav } from "../../components/nav/nav";
import { GraphView } from '../../components/graph/graphView'
import { ArrowLink } from "../../components/arrowLink/arrowLink"
import { Button } from '../../components/button/button';
import { Modal } from '../../components/modals/modal';

import "./GraphDitailsPage.css"

export const GraphDitailsPage = () =>{
    const navigate = useNavigate();
    const { id } = useParams()

    const [graphDitails, setGraphDitails] = useState({})
    const [isModalVisible, setModalVisible] = useState(false);
    const dispatch = useDispatch()

    useEffect(()=>{
        //Инициализация данных
        dispatch(initialState())
        setModalVisible(false)

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

    const AddCurrentVeridy = (values) =>{
        dispatch(addCurrentVerify({name: Object.keys(values)[0], value: values[Object.keys(values)[0]]}))
    }

    const VerifyGraph = useSelector(state=>state.VerifyGraph)
    //console.log(VerifyGraph)

    const addNewRecordHandler = (values) =>{
        //console.log(values)
        const newRecordId = uuidv4();
        const newRecord = {
            id: newRecordId,
            sourseNode_id: values.sourseNode,
            sourseNode_name: graphSchem.schema.nodes.find((node) => node.id === values.sourseNode).name,
            targetNode_id: values.targetNode,
            targetNode_name: graphSchem.schema.nodes.find((node) => node.id === values.targetNode).name,
            statusLink: values.statusLink
        }

        dispatch(addVerifyNode(newRecord))
        setModalVisible(true)
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
                                    <Field name='sourseNode'nodes={graphSchem.schema.nodes} placeholder = "Выберете узел источник"> 
                                        {({ input, meta, ...props }) => (
                                            <div data-err={meta.error && meta.touched}>
                                                <select {...input} {...props} 
                                                    className={(meta.error && meta.touched) ? 'errBorder' : ''}
                                                    onChange={(e) => {
                                                        input.onChange(e); // Обновляем значение в форме
                                                        AddCurrentVeridy({ [input.name]: e.target.value }); // Вызываем функцию с новым значением
                                                    }}
                                                >
                                                    <option value = {""}>{props.placeholder}</option>
                                                    { (props.nodes) ? (
                                                        props.nodes.map((elem) =>
                                                            <option value = {elem.id} name={elem.name} key={elem.id}>{elem.name}</option>
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
                                                <select {...input} {...props} 
                                                    className={(meta.error && meta.touched) ? 'errBorder' : ''}
                                                    onChange={(e) => {
                                                        input.onChange(e); // Обновляем значение в форме
                                                        AddCurrentVeridy({ [input.name]: e.target.value }); // Вызываем функцию с новым значением
                                                    }}
                                                >
                                                    <option value = {""}>{props.placeholder}</option>
                                                    { (props.nodes) ? (
                                                        props.nodes.map((elem) =>
                                                            <option value = {elem.id} name={elem.name} key={elem.id}>{elem.name}</option>
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
                                    <Field name = "statusLink" type='radio' value="0" lable = {numStatusLink[0]}>
                                        {({ input, meta, ...props }) => (
                                                <div className='flex radio-block' >
                                                    <input {...input}/>
                                                    <label>{props.lable}</label>
                                                </div>
                                        )}
                                    </Field>

                                    <Field name = "statusLink" type='radio' value="1" lable = {numStatusLink[1]}>
                                        {({ input, meta, ...props }) => (
                                                <div className='flex radio-block'>
                                                    <input {...input}/>
                                                    <label>{props.lable}</label>
                                                </div>
                                        )}
                                    </Field>

                                    <Field name = "statusLink" type='radio' value="2" lable = {numStatusLink[2]}>
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
        
            <Modal type="notify" text="Запись добавлена успешно!" isOpen={isModalVisible} setIsOpet={setModalVisible}/>
        </div>
    )
}
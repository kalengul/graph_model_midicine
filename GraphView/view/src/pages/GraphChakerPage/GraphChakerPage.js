import React, {useState} from "react"
import axios from "axios";
import { useParams, useNavigate } from 'react-router-dom'
import { deliteVerifyNode} from '../../redux/verifyGraphSlice';
import { useSelector, useDispatch} from 'react-redux';

import { Nav } from "../../components/nav/nav"
import { Button } from "../../components/button/button";
import { ArrowLink } from "../../components/arrowLink/arrowLink";
import {Modal} from "../../components/modals/modal"

import {numStatusLink} from "../../functions/numerators";

import "./GraphChakerPage.css"

export const GraphChakerPage = () =>{
    const { id, schema_name } = useParams()

    const [isModalVisible, setModalVisible] = useState(false)
    const [changeNodeId, setChangeNodeId] = useState("")

    const navigate = useNavigate();
    
    const retunClickHandler = ()=>{
        navigate(`/graphs/${id}`);
    }

    const dispatch = useDispatch()
    const verifyData = useSelector(state => state.VerifyGraph.verifyData)

    //Удаление связей из списка
    const DeleteNode = (id) =>{
        dispatch(deliteVerifyNode({id: id}))
    }

    //Изменение стостояния связи в списке
    const ChandeStatusLink = (id) =>{
        setChangeNodeId(id)
        setModalVisible(true)
    }

    const SaveHandler = async () =>{
        const data = {
            data: JSON.stringify(verifyData),
            graph_id: id
        }
        console.log(data)
        try {
            const response = await axios({ 
                method: "POST", 
                url: "http://localhost:7000/api/graphsvalid/addnew", 
                data,
                headers: { 'Content-Type': 'multipart/form-data'},
            }).then((value)=>alert(value.data)
            ).catch((error)=>{
                alert(error)
            })
            
        } catch (error) {}
    }

    return(
        <div>
            <Nav></Nav>
            <ArrowLink className="flex jc-start" title={`графы | ${schema_name}`} onClick={retunClickHandler}/>
            <div className='flex jc-center'>
                <h1>Результаты проверки графа</h1>
            </div>

            {/* ОТображение списка с инструкциями */}
            <div className='flex jc-center documentation-table'>
                <table>
                    <thead>
                        <tr>
                            <th scope="col">№</th>
                            <th scope="col">Узел источник</th>
                            <th scope="col">Целевой узел</th>
                            <th scope="col">Состояние связи</th>
                            <th scope="col"></th>
                        </tr>
                    </thead>
                    <tbody>
                        {verifyData.map((elem, index)=>
                            <tr key={elem.id} className = "tr-click" >
                                <th>{index+1}</th>
                                <td>{elem.sourseNode_name}</td>
                                <td>{elem.targetNode_name}</td>
                                <td>{numStatusLink[elem.statusLink]}</td>
                                <td>
                                    <Button view="delete" onClick={()=>DeleteNode(elem.id)}/>
                                    <Button view="change" onClick={()=>ChandeStatusLink(elem.id)}/>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
            <Button view="fill" lable = "Сохранить" onClick={SaveHandler}/>
            
            <Modal type="changeLinkStatus" isOpen={isModalVisible} setIsOpet={setModalVisible} id={changeNodeId}/>
        </div>
    )
}
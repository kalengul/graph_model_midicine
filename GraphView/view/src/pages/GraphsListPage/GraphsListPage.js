import React, {useEffect, useCallback, useState} from 'react'
import {useNavigate} from 'react-router-dom'
import axios from 'axios'
import { saveAs } from 'file-saver';

//Components
import { Nav } from "../../components/nav/nav";
import { Button } from '../../components/button/button';

export const GraphsListPage = (props) =>{
    const navigate = useNavigate();
    const [graphSchemes, setGraphSchemes] = useState([])

    useEffect(() => {
        try {
            const response = axios({ 
                method: "GET", 
                url: "http://localhost:7000/api/graphs/all", 
            }).then((res)=>{

                setGraphSchemes(res.data.Data) //Доваление в useState
            })
        } catch (e) {}
      }, [])
    
    const ClickHandler = (e, elem) =>{ navigate(`/graphs/${elem.id}`) }

    const DeleteHandler = async (e, elem) =>{
        const id = elem.id

        try {
            const response = await axios({ 
                method: "DELETE", 
                url: `http://localhost:7000/api/graphs/${id}`, 
            }).then((res)=>{
                setGraphSchemes((prevSchemes) => prevSchemes.filter((scheme) => scheme.id !== id));
                alert(res.data);
            })
        } catch (e) {}
    }

    const DownloadHandler = async (e, elem) =>{
        const id = elem.id
        const fileName = elem.title

        try {
            axios.get(`http://localhost:7000/api/graphs/download/${id}`, {responseType: 'blob'})
            .then((res)=>{
                console.log(res)
                const blob = new Blob([res.data], { type: 'application/pdf' });
                saveAs(blob, fileName);
            })     
        } catch (error) {}
    }

    return(
        <div>
            <Nav></Nav>
            <div className='flex jc-center'>
                <h1>Графы</h1>
            </div>
    
            {/* Отображение списка с инструкциями */}
            <div className='flex jc-center documentation-table'>
                <table>
                    <thead>
                        <tr>
                            <th scope="col">№</th>
                            <th scope="col">Схема</th>
                            <th scope="col">Дата добавления</th>
                            <th scope="col"></th>
                        </tr>
                    </thead>
                    <tbody>
                        {graphSchemes.map((elem, index)=>
                            <tr key={elem.id} className = "tr-click" >
                                <th >{index+1}</th>
                                <td  onClick={(e) => ClickHandler(e, elem)}>{elem.title} </td>
                                <td>{elem.create_data}</td>
                                <td>
                                    <Button view="delete" onClick={(e)=>DeleteHandler(e, elem)}/>
                                    <Button view="download" onClick={(e)=>DownloadHandler(e, elem)}/>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
            
            <Button lable = "Добавить" view="fill" onClick = {(e)=>navigate(`/add/graphschem`)}></Button>
            
        </div>
    )
}
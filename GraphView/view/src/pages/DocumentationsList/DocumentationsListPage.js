import React from 'react'
import { Nav } from "../../components/nav/nav";
import { Button } from '../../components/button/button';


import "./DocumentationsListPage.css"

export const DocumentationsListPage = () =>{
    return(
            <div>
                <Nav></Nav>
                <div className='flex jc-center'>
                    <h1>Документация</h1>
                </div>
        
        
                {/* ОТображение списка с инструкциями */}
                <div className='flex jc-center documentation-table'>
                    <table>
                        <thead>
                            <tr>
                                <th scope="col">№</th>
                                <th scope="col">Название файла</th>
                                <th scope="col">Дата обновления</th>
                                <th scope="col"></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th>1</th>
                                <td>Amiodsron.pdf</td>
                                <td>17.09.2024</td>
                                <td>22</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <Button lable = "Добавить" view="fill"></Button>
                
                
            </div>
    )
}
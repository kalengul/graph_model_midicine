import { useEffect } from 'react'
import axios from 'axios'

import { useDispatch} from 'react-redux';
import {addValue} from '../../redux/DrugGroupManageSlice'
import { RootState } from '../../redux/store';

import "./sideEffectsTable.scss"


export const SideEffectsTable = ()=>{

    return (
    <table className="SE-table table">
     <thead>
            <tr>
                <th scope="col">#</th>
                <th scope="col">ПЭ/ЛС</th>
                <th scope="col">Last</th>
                <th scope="col">Handle</th>
            </tr>
        </thead>
        <tbody>
            <tr>
            <th scope="row">1</th>
            <td>Mark</td>
            <td>Otto</td>
            <td>@mdo</td>
            </tr>
            <tr>
            <th scope="row">2</th>
            <td>Jacob</td>
            <td>Thornton</td>
            <td>@fat</td>
            </tr>
            <tr>
            <th scope="row">3</th>
            <td colspan="2">Larry the Bird</td>
            <td>@twitter</td>
            </tr>
        </tbody>
    </table>
    )
}
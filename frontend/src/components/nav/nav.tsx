import { useEffect } from 'react'
import axios from 'axios'

import { useDispatch, useSelector} from 'react-redux';
import {addValue, initStates} from '../../redux/MenuSlice'

import "./nav.scss"

interface INavProps{
    isActive?: string
}

export const Nav = (props: INavProps)=>{
    const dispatch = useDispatch()

    //
    useEffect(()=>{
        dispatch(initStates())
        axios({ 
            method: "GET", 
            url: "/api/getMenu/", 
        }).then((res)=>{
            console.log(res.data)
            dispatch(addValue({title: "links", value: res.data.data}));
        })
     }, [])

    const menu = useSelector((state)=>state.menu.links)
    console.log(menu)

    return (
        <nav>
            <h1>ТОШ</h1>
            <ul>
                {Array.isArray(menu) && menu.map((elem)=><li>{elem.title}</li>)}
            </ul>
            
        </nav>
    )

}
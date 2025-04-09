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

    dispatch(initStates())
    useEffect(()=>{
        console.log("Подключение")
        axios({ 
            method: "GET", 
            url: "/api/getMenu/", 
        }).then((res)=>{
            console.log(res.data)
            dispatch(addValue({title: "links", value: res.data}));
        })
    }, [])

    const menu = useSelector((state)=>state.menu.links)

    return (
        <nav>
            <ul>
                {menu.map((link)=>{
                    <li>{link.title}</li>
                })}
            </ul>
            
        </nav>
    )

}
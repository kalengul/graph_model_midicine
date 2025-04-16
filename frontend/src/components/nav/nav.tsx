import { useLocation  } from 'react-router-dom';
import { useEffect } from 'react'
import axios from 'axios'

import { useDispatch, useSelector} from 'react-redux';
import {addValue, initStates} from '../../redux/MenuSlice'
import { RootState } from '../../redux/store';

import "./nav.scss"

export const Nav = ()=>{
    const dispatch = useDispatch()
    const location = useLocation();

    useEffect(()=>{
        dispatch(initStates())
        axios({ 
            method: "GET", 
            url: "/api/getMenu/", 
        }).then((res)=>{
            // console.log(res.data)
            dispatch(addValue({title: "links", value: res.data.data}));

            const locat: string = location.pathname

            dispatch(addValue({title: "isActive", value: locat}));

        })
     }, [])


    const menu = useSelector((state: RootState)=>state.menu.links)
    const activeLink = useSelector((state: RootState)=>state.menu.isActive)

    return (
        <nav className='flex-column flex-shrink-0 p-3 sticky-top me-3 mainNav'>
            <h1>ТОШ</h1>
            <hr />
            <ul className="nav nav-pills flex-column mb-auto">
                {Array.isArray(menu) && menu.map((elem)=>
                    <li className='nav-item mb-3 nav-main'>
                        <a href={elem.slug} className={(activeLink==elem.slug)? 'nav-link link-dark active' : 'nav-link link-dark'}>
                            {elem.title}
                        </a>
                    </li>
                )}
            </ul>

        </nav>
    )

}
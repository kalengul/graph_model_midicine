import { useLocation  } from 'react-router-dom';
import { useEffect } from 'react'

import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import {fetchMenu} from '../../redux/MenuSlice'
import {addValue, initStates} from '../../redux/MenuSlice'

import "./nav.scss"

export const Nav = ()=>{
    const dispatch = useAppDispatch()
    const location = useLocation();

    useEffect(()=>{
        dispatch(initStates())//Инициализация состояний
        dispatch(fetchMenu()) //Получение меню с сервера

        const locat: string = location.pathname
        dispatch(addValue({title: "isActive", value: locat}));

    }, [dispatch, location])


    const menu = useAppSelector((state)=>state.menu.links)
    const activeLink = useAppSelector((state)=>state.menu.isActive)

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
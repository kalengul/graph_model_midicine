import { useLocation  } from 'react-router-dom';
import { useEffect, useMemo} from 'react'

import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import {fetchMenu, addValue} from '../../redux/MenuSlice'

import "./nav.scss"

export const Nav = ()=>{
    const dispatch = useAppDispatch()
    

    const menu = useAppSelector((state)=>state.menu.links)
    const activeLink = useAppSelector((state)=>state.menu.isActive)

    const location = useLocation();
    const locat = useMemo(() => location.pathname, [location.pathname]);


    useEffect(()=>{
        dispatch(fetchMenu()) //Получение меню с сервера
    }, [dispatch])

    useEffect(()=>{
        dispatch(addValue({title: "isActive", value: locat}));
    }, [dispatch, locat])

    return (
        <nav className='flex-column flex-shrink-0 p-3 sticky-top me-3 mainNav'>
            <h1>ТОШ</h1>
            <hr />
            <ul className="nav nav-pills flex-column mb-auto">
                {Array.isArray(menu) && menu.map((elem, index)=>
                    <li className='nav-item mb-3 nav-main' key={index}>
                        <a href={elem.slug} className={(activeLink==elem.slug)? 'nav-link link-dark active' : 'nav-link link-dark'}>
                            {elem.title}
                        </a>
                    </li>
                )}
            </ul>

        </nav>
    )

}
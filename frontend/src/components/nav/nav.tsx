import { useLocation, useNavigate } from 'react-router-dom';
import {useState, useEffect, useMemo} from 'react'

import { useAppDispatch, useAppSelector} from '../../redux/hooks';
import {fetchMenu, addValue} from '../../redux/MenuSlice'

import list from "../../../public/list.svg"
import person from "../../../public/person-circle.svg"

import "./nav.scss"
import { logout } from '../../redux/AuthSlice';

export const Nav = ()=>{
    const dispatch = useAppDispatch()
    const navigate = useNavigate();

    const isAuth = useAppSelector(state=>state.auth.isAuthenticated)
    const user = useAppSelector(state=>state.auth.user)

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

    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const toggleMenu = () => { //Отскрытие и скрытие меню
        setIsMenuOpen(!isMenuOpen);
    };

    return (
        <>
            <nav className={`flex-column flex-shrink-0 p-3 sticky-top me-3 mainNav ${isMenuOpen ? "mobilePosition" : ""}`}>
                <div className="burger-menu" onClick={toggleMenu}>
                    <div className='w-100 flex jc-end'>
                        <img src={list} className={isMenuOpen ? "menuOpen" : ""}/>
                    </div>
                </div>

                <div className={`mobile-nav ${isMenuOpen ? 'mobile-open' : ''}`}>                
                    <h1 className='logo' onClick={()=>navigate("/")}>ТОШ</h1>
                    <hr />

                    {isAuth &&
                        <div className='userinfo mb-5 flex ai-center fd-column'>
                            <img src={person} alt="person"/>
                            <p className='mb-0 username'>{user.username?.toLocaleUpperCase()}</p>
                            <p className='mb-0 userrole'>{user.role}</p>
                        </div>
                    }

                    <ul className="nav nav-pills flex-column mb-auto">
                        {Array.isArray(menu) && menu.map((elem, index)=>
                            (elem.slug === "/dataManage") ?
                            ( isAuth &&
                                <li className='nav-item mb-3 nav-main' key={index}>
                                    <a href={elem.slug} className={(activeLink==elem.slug)? 'nav-link link-dark active' : 'nav-link link-dark'}>
                                        {elem.title}
                                    </a>
                                </li>
                            ) :
                            <li className='nav-item mb-3 nav-main' key={index}>
                                <a href={elem.slug} className={(activeLink==elem.slug)? 'nav-link link-dark active' : 'nav-link link-dark'}>
                                    {elem.title}
                                </a>
                            </li>
                        )}

                        <div className='nav-footer'>
                            {
                                !isAuth ? 
                                <li className='nav-item mb-5 nav-main'>
                                    <a href="/login" className='nav-link link-dark link-login'> Войти </a>
                                </li>
                                :
                                <li className='nav-item mb-5 nav-main'>
                                    <a onClick = {()=>dispatch(logout())} className='nav-link link-dark link-login'> Выйти </a>
                                </li>
                            }
                        </div>
                    </ul>
                </div>
            </nav>
        </>
    )

}
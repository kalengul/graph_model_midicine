import {useNavigate} from 'react-router-dom'
import "./nav.css"

export const Nav = (props)=>{
    const navigate = useNavigate();

     //Переходы на страницы
     const navigateInstructions = () => { navigate('/instructions') };
     const navigateDocumentations = () => { navigate('/documentations') };
     const navigateGraphs = () => { navigate('/graphs') };


    return(
        <div>
            <nav className="flex align-center jc-end ">
                <ul className="flex nav-ul">
                    <li className={"nav-li"} onClick = {navigateGraphs}>Графы</li>
                    <li className={"nav-li"} onClick={navigateDocumentations}>Документация</li>
                    <li className={"nav-li"} onClick = {navigateInstructions}>Инструкции</li>
                </ul>
            </nav>
        </div>
    )
}
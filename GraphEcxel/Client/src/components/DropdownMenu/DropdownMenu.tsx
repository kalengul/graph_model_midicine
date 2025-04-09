import "./DropdownMenu.scss"

const DropdownMenu = (props) =>{
   
    switch (props.typeDropdownMenu) {
        case "tableDataManagement":
            const CssClasses: string =`dropdown-menu ${props.className || ''}`.trim();
            return (
                <ul className={CssClasses}>
                    <li><a className="dropdown-item" href="#">Изменить</a></li>

                    <li><hr className="dropdown-divider" /></li>

                    {(props.isHasFile!=null) && 
                        <>
                            <li><a className="dropdown-item" href="#">Экспортировать в .json</a></li>
                            <li><a className="dropdown-item" href="#">Экспортировать в .html</a></li>
                        </>
                    }

                    <li><hr className="dropdown-divider" /></li>
                    <li><a className="dropdown-item" href="#">Удалить </a></li>
                </ul>
            )
            default:
                break;
    }
}

export default DropdownMenu
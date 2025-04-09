import plusCircle from "../../assets/plus-circle.svg"
import pencilSquare from "../../assets/pencil-square.svg"
import threeDots from "../../assets/three-dots.svg"
import download from "../../assets/download.svg"
import trash3 from "../../assets/trash3.svg"


import "./button.scss"

function Button(props) {
    let CssClasses: string;
    switch (props.typeBtn) {
        case "Primary_btn":
            CssClasses = `btn btn-primary sh-m btn-br-m ${props.className || ''}`.trim()
            return (
                <button className={CssClasses} type="submit" onClick={props.onClick} disabled={props.disabled}>{props.children}</button>
            )
        case "Light_btn":
            CssClasses = `btn btn-light btn-sm sh-s btn-br-sm ${props.className || ''}`.trim()
            return(
                <button className={CssClasses} type="submit" onClick={props.onClick} disabled={props.disabled}> {props.children}</button>
            )
        case "Return_btn":
            CssClasses = `btn btn-light btn-sm sh-s btn-br-sm ${props.className || ''}`.trim()
            return(
                <button className={CssClasses} type="submit" onClick={props.onClick} disabled={props.disabled}> {props.children}</button>
            )
        case "Add_icon":
            CssClasses = `btn-icon-m ${props.className || ''}`.trim()
            return (
                <img className={CssClasses} alt="plusCircle" src={plusCircle} onClick={props.onClick}/>
            )  
        case "Change_icon":
            CssClasses = `btn-icon-m ${props.className || ''}`.trim()
            return (
                <img className={CssClasses} alt="pencilSquare" src={pencilSquare} onClick={props.onClick}/>
            )       
        case "Three-dots_icon":
            CssClasses = `btn-icon-s ${props.className || ''}`.trim()
            return (
                <img className={CssClasses} data-bs-toggle={props.dataBsToggle} aria-expanded={props.ariaExpanded} alt="threeDots" src={threeDots} onClick={props.onClick}/>
            )
        case "Download_icon":
            CssClasses = `btn-icon-s ${props.className || ''}`.trim()
            return (
                <img className={CssClasses} data-bs-toggle={props.dataBsToggle} aria-expanded={props.ariaExpanded} alt="download" src={download} onClick={props.onClick}/>
            )
        case "Delete_icon":
            CssClasses = `btn-icon-s ${props.className || ''}`.trim()
            return (
                <img className={CssClasses} data-bs-toggle={props.dataBsToggle} aria-expanded={props.ariaExpanded} alt="trash3" src={trash3} onClick={props.onClick}/>
            )
            default:
                break;
    }
}

export default Button
import { useState } from 'react';
import { ISE } from "../../redux/ComputationSlice"
import "./collapsList.scss"

interface ICollapsListProps{
    title?: string;
    className?: string
    type: "riscs"|"drugs-combin"
    content: ISE[] | string[] |undefined
}

export const CollapsList = (props: ICollapsListProps) =>{
    const [isExpanded, setIsExpanded] = useState(false);
    
    if(props.content) {
        if (props.content.length === 0) return (<></>) 
        // Определяем, нужно ли показывать кнопку "Показать еще"
        const shouldShowToggle = props.content.length > 3;
        // Определяем, сколько элементов показывать (все или только 3)
        const visibleItems = shouldShowToggle && !isExpanded ? props.content.slice(0, 3) : props.content;

        return (
            <div className={props.className}>
                <h6>{props.title}</h6>
                {props.type === "riscs" ? 
                    (visibleItems as ISE[]).map((e, index) => (
                        <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                            <div>
                                <span className='me-3'>{index+1}.</span> 
                                <span>{e.se_name}</span>
                            </div>
                            <span>{e.rank}</span>
                        </div>
                    ))
                :
                (props.type === "drugs-combin" && 
                    (visibleItems as string[]).map((d, index)=>
                        <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                            <div>
                                <span className='me-3'>{index+1}.</span> 
                                <span>{d}</span>
                            </div>
                        </div>
                    )
                )
                }

                {shouldShowToggle && (
                    <button 
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="btn toggle-btn mt-3" // добавьте свои стили
                    >
                        {isExpanded ? 'Скрыть' : `Показать еще (${props.content.length - 3})`}
                    </button>
                )}
            </div>
        )
    }
    else return (<></>)
}
import { useState } from 'react';
import { ISE, ICompareData, ISEFromDrug} from "../../redux/ComputationSlice"
import {IDrugCombinationWithSE} from "../../redux/Interfaces"
import "./collapsList.scss"

interface ICollapsListProps{
    title?: string;
    className?: string
    type: "riscs"|"compare-riscs"|"drugs-combin"|"riscs-from-drug"|"drugs-combin-fortran"
    content: ISE[] | string[] | ICompareData[] | ISEFromDrug[]| IDrugCombinationWithSE[] | undefined

    visibleRisks: boolean
}

const RenderItem = (type: ICollapsListProps['type'], item: any, index: number, visibleRisks: boolean) =>{

    switch (type) {
        case "riscs": {
            const riscItem = item as ISE;
            return(
                <>
                <div className={`flex jc-sb w-100 ps-3 pe-3 ${index===0 && "mt-3"}`} key={index}>
                    <div>
                        <span className='me-3'>{index+1}.</span> 
                        <span>{riscItem.se_name}</span>
                    </div>
                    {visibleRisks && <span>{riscItem.rank}</span>}
                </div>
                <hr/>
                </>
            )
        }
        case "compare-riscs":{
            const compareItem = item as ICompareData;

            return (
                <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                    <div>
                        <span className='me-3'>{index + 1}.</span> 
                        <span>{compareItem.se_name}</span>
                    </div>
                    {visibleRisks && <div className='w-25 flex jc-sb'>
                        <span>{compareItem.rankBayes}</span>
                        <span className='ms-3'>{compareItem.rankFortran}</span>
                    </div>}
                </div>
            );
        }
        case "drugs-combin":
            return (
                <div className='flex jc-sb w-100 ps-3 pe-3' key={index}>
                    <div>
                        <span className='me-3'>{index + 1}.</span> 
                        <span>{item}</span>
                    </div>
                </div>
            );
        case "drugs-combin-fortran":{
            const drugItem = item as  IDrugCombinationWithSE;
            return (
                <>
                <div className={`drugs-combin-fortran-Container w-100 ps-3 pe-3 ${index===0 && "mt-3"}`} key={index}>
                    <div className="drugs-list">
                        <span className='me-3'>{index + 1}.</span> 
                        <span>{drugItem.name}</span>
                    </div>
                    <div className="drugsSE-list">
                        {drugItem.side_effects && drugItem.side_effects.length> 0 &&<>
                        <span>Есть риск появления побочных эффектов:</span>
                        <div >
                            {drugItem.side_effects.length>0 && drugItem.side_effects.map((se, se_index) =>
                            <div className='flex jc-sb'>
                                <div>
                                    <span className='me-3'>{se_index + 1}.</span> 
                                    <span>{se.se_name}</span>
                                </div>
                                {visibleRisks && <span>{se.rank}</span>}
                            </div>)
                            }
                        </div>
                        </>}
                    </div>
                </div>
                <hr/>
                </>
            );
        }
        default:
            return null;
    }
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
                <div className='ps-3'>
                    <h6>{props.title}</h6>
                </div>

                {visibleItems.map((item, index) => 
                    RenderItem(props.type, item, index, props.visibleRisks)
                )}
                
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
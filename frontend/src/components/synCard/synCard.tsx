import styled from 'styled-components';
import { useAppDispatch } from '../../redux/hooks';
import {changeSynStatus} from "../../redux/SynonymsSlice"


interface ISynCardProps {
    id: string
    s_name: string
    index: number
    bgColor: string | undefined
}

interface IStileDiveProps {
    $BgColor: string | undefined;
}

export const SynCard = (props: ISynCardProps) =>{
    const dispatch = useAppDispatch()
    const StyledDiv = styled.div<IStileDiveProps>`
        background-color: ${props => props.$BgColor};
    `;

    const clickHandler =(s_id: string)=>{
        console.log(props)
        dispatch(changeSynStatus(s_id))
    }

    return (
        <StyledDiv $BgColor={props.bgColor} className="flex jc-sb w-100 ps-3 pe-3 sunList-elem" key={props.id} onClick={()=>clickHandler(props.id)}>
            <div >
                <span className='me-3'>{props.index}.</span> 
                <span>{props.s_name}</span>
            </div>
        </StyledDiv>
    )
}
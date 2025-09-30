import {IComputationFortran } from '../../redux/ComputationSlice';

// export interface IComputationFortranData{
//     se_name?: string
// }

interface IErrors{
    se_name?: string,
}


export const ComputationFortranValidator = (values: IComputationFortran)=>{
    const errors: IErrors = {}
    if(values) return errors
    //  console.log(values)
    return errors
}

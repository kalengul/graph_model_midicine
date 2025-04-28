import {IComputationFortran } from '../../redux/ComputationSlice';

// export interface IComputationFortranData{
//     se_name?: string
// }

interface IErrors{
    se_name?: string,
}


export const ComputationFortranValidator = (values: IComputationFortran)=>{
    const errors: IErrors = {}
     console.log(values)
    return errors
}

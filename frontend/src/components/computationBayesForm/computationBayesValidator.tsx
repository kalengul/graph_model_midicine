import {IComputationBayes } from '../../redux/ComputationSlice';

// export interface IComputationFortranData{
//     se_name?: string
// }

interface IErrors{
    se_name?: string,
}


export const ComputationBayesValidator = (values: IComputationBayes)=>{
    const errors: IErrors = {}
     console.log(values)
    return errors
}

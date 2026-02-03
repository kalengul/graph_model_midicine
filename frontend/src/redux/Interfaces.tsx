export interface IResultBayes {
  сompatibility_bayes: string ,
  rank_iteractions: number | undefined,
  side_effects: ISideEffectComputation[],
  SEFromDrug: ISEFromDrug[],
  combinations: IDrugCombination[] | undefined
  drugs: string[]
}

export interface IResultFortran{
  сompatibility_fortran: string,
  rank_iteractions: number | undefined,
  side_effects: ISideEffectComputation[],
  combinations: IDrugCombination[] | undefined
  SEFromDrug: ISEFromDrug[],
  drugs: string[]
}

export interface IComputationElem {
  id: string,
  drug_name: string,
  dg_id: string,
}

export interface ISEFromDrug{
  d_name: string,
  effects: ISE[]
}

export interface ISE{
  se_name: string,
  rank: number,
}

export interface ISideEffectComputation{
  сompatibility: string,
  effects: ISE[]
}

interface IDrugCombination{
  сompatibility: string
  drugs: string[]
}


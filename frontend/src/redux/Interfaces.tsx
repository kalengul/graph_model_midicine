export interface IResultBayes {
  compatibility_bayes: string ,
  rank_iteractions: number | undefined,
  side_effects: ISideEffectComputation[],
  SEFromDrug: ISEFromDrug[],
  combinations: IDrugCombination[] | undefined
  drugs: string[]
}

export interface IBannedPair{
  pair: string[]
  comment: string | null
}

export interface IBannedPairCont{
  contraindications: string[]
  drug: string
}

export interface IResultFortran{
  compatibility_fortran: string,
  rank_iteractions: number | undefined,
  side_effects: ISideEffectComputation[],
  combinations: IDrugCombination[] | undefined
  SEFromDrug: ISEFromDrug[],
  drugs: string[]
  bannedPairs: IBannedPair[],
  bannedPairsCont: IBannedPairCont[]
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
  compatibility: string,
  effects: ISE[]
}

interface IDrugCombination{
  compatibility: string
  drugs: string[]
}


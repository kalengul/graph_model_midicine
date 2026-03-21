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
  combinations: IDrugCombinationFortran[] | undefined
  SEFromDrug: ISEFromDrug[],
  drugs: string[]
  bannedPairs: IBannedPair[],
  bannedPairsCont: IBannedPairCont[]
  rep_recommendations?: IRepRecommendation[] | undefined
}

export interface IRepRecommendation{
  group_name: string
  drugs: IRepalceDrugs[]
}

export interface IRepalceDrugs{
  drug_name: string
  replace_drugs: string[]
}

export interface IComputationElem {
  id: string,
  drug_name: string,
  nosology_id: string,
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


export interface IDrugCombinationWithSE{
  name: string,
  side_effects: ISE[]
}

interface IDrugCombinationFortran{
  compatibility: string
  drugs: IDrugCombinationWithSE[]
}


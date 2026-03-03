export interface ISelectedType {
    id: number,
    value: string,
    title: string,
}

export const SelectedType: ISelectedType[] = [
    { id: 1, value: "descendingB", title: "По убыванию риска Bayes"},
    { id: 2, value: "ascendingB", title: "По возрастанию риска Bayes"},
    { id: 3, value: "alphabet", title: "По алфавиту"},
    // { id: 4, value: "ascendingF", title: "По возрастанию риска Fortran"},
    // { id: 5, value: "descendingF", title: "По убыванию риска Fortran"},
    
]
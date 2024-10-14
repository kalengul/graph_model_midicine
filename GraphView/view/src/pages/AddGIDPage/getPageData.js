export const GetData = (id) =>{
    const pageData = {
        graphschem: {
            title: 'Добавить схему',
            returnLink: `/graphs`,
            returnLinkTitle: 'графы'
        }
    }

    switch (id) {
        case "graphschem":
            return pageData.graphschem
    
        default:
            return undefined
    }
}
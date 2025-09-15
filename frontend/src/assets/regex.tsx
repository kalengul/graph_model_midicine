export const isRegex = (str: string, regexType: "banned")=>{
    switch (regexType) {
        case "banned": {
            const regex: RegExp = /^banned(-.*)?$/
            return regex.test(str)
        }
        default:
            return false;
    }
} 
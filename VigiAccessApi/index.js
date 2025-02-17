const fs = require('fs')

class VigiAccessParse {
    constructor(parameters) {
        console.log("VigiAccess parse - https://www.vigiaccess.org/");
    }

    //Первый инпут
    //<input class="is-checkradio" type="checkbox" id="accept-terms-and-conditions" wfd-id="id0"></input>
    POST1 = async ()=>{
        const request = new Request('https://www.vigiaccess.org/protocol/IProtocol/search', {
            method: 'POST',
            body: ["aspirin"],
          });
        const response = await fetch(request);
        console.log(response.body)
    }
}

const vigiAccessParse = new VigiAccessParse()
vigiAccessParse.POST1();




// fs.writeFile('./Data/data.txt', JSON.stringify(data, null, 2), (err) => {
//     if (err) throw err;
//     console.log('Данные успешно записаны в data.json');
//   });
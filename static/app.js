import API_KEY from "secret";
console.log("Did my api key make it?", API_KEY);





let country_select = document.getElementById('country');
let state_select = document.getElementById('state');
let city_select = document.getElementById('city');

country_select.onchange = function() {
    country = country_select.value;
    
    fetch('/country/' + country).then(function(response) {
        response.json().then(function(data) {
            let option = "";
            
            for(let state of data.states) {
                option += '<option value="' + state.id + '">' + state.name + '</option>';
            }
            state_select.innerHTML = option;
        });
    });
}

state_select.onchange = function() {
    state = state_select.value;

    fetch('/state/' + state).then(function(response) {
        response.json().then(function(data) {
            let option = "";
            
            for(let city of data.cities) {
                option += '<option value="' + city.id + '">' + city.name + '</option>';
            }
            city_select.innerHTML = option;
        });
    });
}
// async function processForm(evt) {
//     evt.preventDefault();

//     let country = $("#Country").val();
//     let state = $("#State").val();
//     let city = $("#City").val();

//     const response = await axios.post('/search-venues', {country, state, city});

//     return handleResponse(response);
// }

// /** handleResponse: deal with response from our lucky-num API. */

// function handleResponse(resp) {
//     if(resp.data.errors) {
//         for(err in resp.data.errors) {
//             $(`#${err}-err`).append(resp.data.errors[err]); 
//         }
//     }
//     else {
        
//         let lucky = `<p>Your lucky number is ${resp.data.num.num}.  ${resp.data.num.fact}.</p>
//                      <p>Your birth year is ${resp.data.year.year}.  ${resp.data.year.fact}.</p>`

//         $("#lucky-results").append(lucky);
//         $("#lucky-form").trigger('reset');
//     }

// }


// $("#search-venues-form").on("submit", processForm);
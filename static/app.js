async function toggleFavorite(evt) {
    const target = evt.target.closest('i');
    console.log("target class name", target.className)
    const venName = target.closest('i').id;
    console.log("venue name", venName);
    // const story = storyList.stories.find(s => s.storyId === storyId);
  
    if(target.className === "far fa-heart"){
      target.className = "fas fa-heart";
      axios({
        method: 'POST',
        url: '/favorites/add',
        data: {
          venue_name: venName,
        }
      });
    } 
    else if(target.className === "fas fa-heart"){
      target.className = "far fa-heart";
      axios({
        method: 'DELETE',
        url: '/favorites/delete',
        data: {
          venue_name: venName,
        }
      });    
    }
  } 
  
  $("span").on("click", "i", toggleFavorite);
//   $("span").on("click", "i", toggleFavorite);



// CSRF token for JS axios requests 

// axios.defaults.headers.common["X-CSRFToken"] = "{{ csrf_token() }}";

// var csrf_token = "{{ csrf_token() }}";

//     $.ajaxSetup({
//         beforeSend: function(xhr, settings) {
//             if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
//                 xhr.setRequestHeader("X-CSRFToken", csrf_token);
//             }
//         }
//     });
//////////////////////////////////////////////////
//                                              //
//      JS for dynamic SelectField options      //
//      on Venue Search Form.                   //
//                                              //
//////////////////////////////////////////////////

// let country_select = document.getElementById('country');
// let state_select = document.getElementById('state');
// let city_select = document.getElementById('city');

// country_select.onchange = function() {
//     country = country_select.value;
    
//     fetch('/country/' + country).then(function(response) {
//         response.json().then(function(data) {
//             let option = "";
            
//             for(let state of data.states) {
//                 option += '<option value="' + state.id + '">' + state.name + '</option>';
//             }
//             state_select.innerHTML = option;
//         });
//     });
// }

// state_select.onchange = function() {
//     state = state_select.value;

//     fetch('/state/' + state).then(function(response) {
//         response.json().then(function(data) {
//             let option = "";
            
//             for(let city of data.cities) {
//                 option += '<option value="' + city.id + '">' + city.name + '</option>';
//             }
//             city_select.innerHTML = option;
//         });
//     });
// }


///////////////////////////////////////////
//                                       //
//      JS handling submission of        //
//      VenueSearchForm.                 //
//                                       //
///////////////////////////////////////////


async function processForm(evt) {
    evt.preventDefault();

    let country = $("#Country").val();
    let state = $("#State").val();
    let city = $("#City").val();

    console.log("before axios request");
    
    const response = await axios.post('/search-venues', {country, state, city});
    console.log("after axios request");
    console.log(response);
    return handleResponse(response);
}

/** handleResponse: deal with response from our route call to Ticketmaster API. */

function handleResponse(resp) {
    if(resp.data.errors) {
        for(err in resp.data.errors) {
            $(`#${err}-err`).append(resp.data.errors[err]); 
        }
    }
    else {
        for(venue in resp.data) {
            let li = `<li>${venue}</li>`;
            $("#venue-results").append(li);
        }
        // let lucky = `<p>Your lucky number is ${resp.data.num.num}.  ${resp.data.num.fact}.</p>
        //              <p>Your birth year is ${resp.data.year.year}.  ${resp.data.year.fact}.</p>`

        // $("#lucky-results").append(lucky);
        // $("#lucky-form").trigger('reset');
    }

}


// $("#search-venues-form").on("submit", processForm);
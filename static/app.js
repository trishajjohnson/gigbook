////////////////////////////////////////////
//                                        //
//   Code for adding/deleting favorites   //
//   from the database on the search      //
//   venues page as well as the user      //
//   profile page.                        //
//                                        //
////////////////////////////////////////////

async function toggleFavorite(evt) {
  
  evt.preventDefault();
  
  const button = evt.target.closest('button');
  const venName = button.id;

  //  Handling click action for adding/deleting favorites from the Search Venue page.

  if(button.className === "btn btn-dark add-delete" && button.innerHTML.includes("heart")){
    
    const response = await axios({
      method: 'POST',
      url: '/favorites/add',
      data: {
        venue_name: venName,
      }
    });

    if(response.data["result"] === "True") {

      button.className = "btn btn-danger add-delete";
      button.innerHTML = "<i style='color: white;' class='fas fa-heart'></i>";
      
    }

  } 

  else if(button.className === "btn btn-danger add-delete" && button.innerHTML.includes("heart")){
    
    const response = await axios({
      method: 'DELETE',
      url: '/favorites/delete',
      data: {
        venue_name: venName,
      }
    });

    if(response.data["result"] === "True") {
      button.className = "btn btn-dark add-delete";
      button.innerHTML = "<i style='color: greenyellow;' class='far fa-heart'>";
      
    }

  }

  // Handling click action for deleting favorites from User profile page.

  else if(button.className === "btn btn-danger add-delete" && button.innerHTML.includes("trash")){
    
    const response = await axios({
      method: 'DELETE',
      url: '/favorites/delete',
      data: {
        venue_name: venName,
      }
    });

    if(response.data["result"] === "True") {
      
      const li = evt.target.closest('li');
      li.className = "hide";
      
    }
    
  }

} 

// click listener for adding/deleting favorites from Search Venue page
// as well as User profile page under Favorite Venues list.

$(".add-delete").on("click", toggleFavorite);


//////////////////////////////////////////////////
//                                              //
//      JS for dynamic SelectField options      //
//      on Venue Search Form.                   //
//                                              //
//           *** Task for later ***             //
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
//      VenueSearchForm with axios.      //
//      (Need to figure out CSRF issue   //
//      in order to use WTForms with     //
//      axios.)                          //
//                                       //
//         *** Task for later ***        //
//                                       //
///////////////////////////////////////////


// async function processForm(evt) {
//     evt.preventDefault();

//     let country = $("#Country").val();
//     let state = $("#State").val();
//     let city = $("#City").val();

//     console.log("before axios request");
    
//     const response = await axios.post('/search-venues', {country, state, city});
//     console.log("after axios request");
//     console.log(response);
//     return handleResponse(response);
// }

/** handleResponse: deal with response from our route call to Ticketmaster API. */

// function handleResponse(resp) {
//     if(resp.data.errors) {
//         for(err in resp.data.errors) {
//             $(`#${err}-err`).append(resp.data.errors[err]); 
//         }
//     }
//     else {
        
//       for(venue in resp.data) {
//             let li = `<li>${venue}</li>`;
//             $("#venue-results").append(li);
//         }
        
//     }

// }


// $("#search-venues-form").on("submit", processForm);
//  JavaScript to support the operation of the ArcheoLogic Visualier website
//  January 2020
//  Student Number 9217953

    function processSpatialForm2(f) {

      //  This function takes a spatial search form as an argument, and processes
      //  it to identify finds within a certain radius of a central point

      //  NOTE:  All calcalations are done using arbitrary Map Units

      // First clear the map and tables for a clean slate
      clearMap();
      clearTables();

      // Set up variables by getting user input data from the form
      var centre_x = f.centre_x.value  // search centre point x-coordinate
      var centre_y = f.centre_y.value  // search centre point y-coordinate
      var radius = f.radius.value      // search radius

      // Get all find x and y coordinates by selecting table cells with a class of "x" or "y"
      var find_x_elements = document.querySelectorAll('td[class^="x"]')
      var find_y_elements = document.querySelectorAll('td[class^="y"]');

      // A variable to keep track of how many finds are identified
      var finds_found = 0;


      // Loop through the x and y elements, convert the text to integer values,
      // then perform simple Pythagorean geometry to identify those within a certain radius
      for (i=0; i < find_x_elements.length; i++) {
          let x = parseInt(find_x_elements[i].innerText, 10);
          let y = parseInt(find_y_elements[i].innerText, 10);
          let y_difference = Math.abs(y - centre_y);
          let x_difference = Math.abs(x - centre_x);
          let straight_line_distance = Math.sqrt(Math.pow(x_difference, 2) + Math.pow(y_difference, 2))
          //  If a find is closer than or equal to the radius set, run through this code:
          if (straight_line_distance <= radius){
            finds_found +=1;
            var find_number = i+1;
            var local_find_id = ("find").concat(find_number);
            setSelectedFromFindID(local_find_id);  //  Calls JS function to set the find as selected and show it on the map and tables
            //  Console.log used for debugging
            console.log("Find ", i+1 , "is within ", radius, "map units of the centre point and has find_id of ", local_find_id)
          }
       }
       //  If no successful finds were identified, clear the map from any previous selections, and alert the user to try again:
       if (finds_found == 0) {
          clearMap();
          var alert_string = ("No match within " + radius + " map units of (" + centre_x + "," + centre_y + ") : please try again...");
          alert(alert_string);
       }
       return false
      }


    function processSpatialForm(f) {

      //  This function takes a spatial search form as an argument, and processes
      //  it to identify finds that fall within the search area, a rectangle
      //  defined by the x,y coordinates of the lower left and top right corners.

      //  NOTE:  All calcalations are done using arbitrary Map Units

      // First clear the map and tables for a clean slate
      clearMap();
      clearTables();

      //  Set up variables by getting user input data from the form
      //  In this case they represent the lower left and upper right coordinates
      //  of the search area
      var lowleftx = f.lowleftx.value
      var lowlefty = f.lowlefty.value
      var highrightx = f.highrightx.value
      var highrighty = f.highrighty.value

    // Get all find x and y coordinates by selecting table cells with a class of "x" or "y"
      var find_x_elements = document.querySelectorAll('td[class^="x"]')
      var find_y_elements = document.querySelectorAll('td[class^="y"]');

      //  Loop through the find x, y coordinates and check if that find falls within
      //  the search rectangle (NOTE: or right on the border of it!)
      for (i=0; i < find_x_elements.length; i++) {
          let x = parseInt(find_x_elements[i].innerText, 10);  //  converts text string to integer
          let y = parseInt(find_y_elements[i].innerText, 10);
          //  Search logic :  && operator is used to match all conditions
          if ((x >= lowleftx) && (x <= highrightx) && (y >= lowlefty) && (y <= highrighty)){
            var find_number = i+1;
            var local_find_id = ("find").concat(find_number);
            setSelectedFromFindID(local_find_id);  //  Trigger JS function to handle selecting this find
            console.log("Find ", find_number , "is in the search area and has find_id of ", local_find_id)
          }
       }
       return false
      }


    function clearMap() {

        //  This funtions simply identifies all Fields and Finds marked as "selected"
        //  by including the class of "find_selected" or "field_selected", and loops through
        //  each one to reset the class to "find" or "field" respectively

        var selected_fields = document.querySelectorAll('rect[class^="field_selected"]')
        var selected_finds = document.querySelectorAll('circle[class^="find_selected"]')

        //  Loop through selected fields on the map, and reset to unselected state
        for (i=0; i<selected_fields.length; i++){
            console.log(selected_fields[i])
            selected_fields[i].setAttribute("class", "field")
        }
        //  Loop through selected finds on the map, and reset to unselected state
        for (i=0; i<selected_finds.length; i++){
            console.log(selected_finds[i])
            selected_finds[i].setAttribute("class", "find")
        }
    }

    function clearTables() {

        //  This funtions simply identifies all field and find table rows that do NOT have a class of "hidden"
        //  (ie are visible), and loops through each one to reset the class to "hidden"

        //  Get all the visible field and find table rows and store in 2 variables
        var field_tablerow_elements = document.querySelectorAll('tr[class=""]');
        var find_tablerow_elements = document.querySelectorAll('tr[class=""]');

        console.log("field_tablerow_elements: ", field_tablerow_elements)
        console.log("find_tablerow_elements: ", find_tablerow_elements)

        //  Loop through all visible field table rows and reset to hidden
        for (i=0; i<field_tablerow_elements.length; i++){
            console.log(field_tablerow_elements[i])
            field_tablerow_elements[i].setAttribute("class", "hidden")
        }
        //  Loop through all visible find table rows and reset to hidden
        for (i=0; i<find_tablerow_elements.length; i++){
            console.log(find_tablerow_elements[i])
            find_tablerow_elements[i].setAttribute("class", "hidden")
        }
    }

    function processFormAll(field_owner, owner_elements, crop_name, crop_elements) {

        //  this function takes user-selected elements and tablerow elements
        //  and compares them to identify fields that match ALL criteria, ie that have both
        //  the chosen owner name and also crop name.

        //  Set up local variables

        var owner_index;
        var crop_index;
        var class_index;

        // Get all field and find table rows by selecting table rows with an id matching the pattern
        var all_field_rows = document.querySelectorAll('tr[id^="tablerow_field"]');
        var all_find_rows = document.querySelectorAll('tr[id^="tablerow_find"]');

        //  Loop through all the rows, and get local variables from their children elements
        //  NOTE: The children elements are the <td> elements ie the individual cells in the tables
        //  (ie to "get inside" the table rows and extract info, then set variables equal to that info)
        //  Note also that the trim() and toUpperCase() functions are used to "clean" up and standardise the data
        for (i=0; i < all_field_rows.length; i++) {
            let this_field = ("field").concat(all_field_rows[i].children[0].innerText.trim());
            let this_owner = all_field_rows[i].children[1].innerText.trim().toUpperCase();
            let this_crop = all_field_rows[i].children[6].innerText.trim().toUpperCase();
            let finds_in_this_field = all_field_rows[i].children[7].innerText.trim();
            if ((field_owner == this_owner) && (crop_name == this_crop)){
              console.log("Match FOUND");  //  Console logging only used for debugging
              setSelectedFromFieldID(this_field);  //  Use external JS function to set the field as selected
            } else {
              console.log("NO MATCH")
            }
          }
      return false;
    }

    function processFormAny(field_owner, owner_elements, crop_name, crop_elements) {

      //  this function takes user-selected elements and tablerow elements
      //  and compares them to identify fields that match ANY criteria, ie that have either
      //  the chosen owner name or crop name.  Those that are matched are selected.

      //  Loop through all the owner attributes in each field tablerow, and
      //  check if the user selected owner is the same.  If so, select that field.
      //  In order to go "up one" from owner elements to a field element, the parentElement operator is used.
      //  Note also that the trim() and toUpperCase() functions are used to "clean" up and standardise the data
        for (i=0; i < owner_elements.length; i++){
            if(owner_elements[i].outerText.toUpperCase().trim() == field_owner.trim()) {
                  owner_elements[i].parentElement.setAttribute("class", "");
                  var parent_id = owner_elements[i].parentElement.getAttribute("id").split('_')[1];
                  setSelectedFromFieldID(parent_id);
            } else {
                  console.log("went to the owner else...");
            }
        }

        //  Loop through all the crop name attributes in each field tablerow, and
        //  check if the user selected crop is the same.  If so, select that field.
        //  In order to go "up one" from owner elements to a field element, the parentElement operator is used.
        for (i=0; i < crop_elements.length; i++){
            if(crop_elements[i].outerText.toUpperCase().trim() == crop_name.trim()) {
                  crop_elements[i].parentElement.setAttribute("class", "");
                  var parent_id = crop_elements[i].parentElement.getAttribute("id").split('_')[1];
                  setSelectedFromFieldID(parent_id);
            } else {
                  console.log("went to the crop else...");
            }
        }
      }

    function processForm(f){

        //  This function takes a form as an argument and processes that basic search
        //  form.  There are two "routes" depending on which of the radio buttons were selected
        //  by the user (ANY or ALL).

        //  Start with clean slate
        clearMap()
        clearTables()

        //  Set the following variables to the options chosen by the user
        let field_owner = f.option1.value;
        let crop_name = f.option2.value;

        //  Store the state of the radio button in a variable (either 'ALL' or 'ANY')
        let radio_select = f.and_or.value;

        var owner_elements = document.querySelectorAll('td[class^="owner"]');
        var crop_elements = document.querySelectorAll('td[class^="crop_name"]');

        //  Select route (next function) depending on radio button selection
        if (radio_select == 'ALL') {processFormAll(field_owner, owner_elements, crop_name, crop_elements)}
        if (radio_select == 'ANY') {processFormAny(field_owner, owner_elements, crop_name, crop_elements)}

        return false
    }

    function resetForms(){

        //  Gets all forms by ID, and resets them
        //  Also clears the map and tables for good measure

        document.getElementById("main_form").reset();
        document.getElementById("spatial_form").reset();
        document.getElementById("spatial_form2").reset();
        console.log("Resetting the forms....")
        clearMap();
        clearTables();
    }

    function setFieldSelected(id){

        //  Checks if a field is unselected, and if so, selects it,
        //  and vice-versa
        var trow_id = "tablerow_".concat(id.id)
        var trow = document.getElementById(trow_id)
        if (id.getAttribute("class") == "field_selected") {
            id.setAttribute("class", "field");
            trow.setAttribute("class", "hidden");
        } else {
            id.setAttribute("class", "field_selected");
            trow.setAttribute("class", "");
        }
    }

    function setFindSelected(id){

      //  Checks if a field is unselected, and if so, selects it,
      //  and vice-versa
        var trow_id = "tablerow_".concat(id.id)
        var trow = document.getElementById(trow_id)
        if (id.getAttribute("class") == "find_selected") {
            id.setAttribute("class", "find");
            trow.setAttribute("class", "hidden");
        } else {
            id.setAttribute("class", "find_selected");
            trow.setAttribute("class", "")
        }
    }

    function setSelectedFromFindID(find_id){
        //  Takes a find_id (eg find6) and selects that find
        var trow_id = "tablerow_".concat(find_id)
        var trow = document.getElementById(trow_id);
        var this_find = document.getElementById(find_id);
        this_find.setAttribute("class", "find_selected");
        trow.setAttribute("class", "");
    }

    function setSelectedFromFieldID(field_id){
      //  Takes a field (eg field6) and selects that field
        var trow_id = "tablerow_".concat(field_id)
        var trow = document.getElementById(trow_id);
        var this_field = document.getElementById(field_id);
        this_field.setAttribute("class", "field_selected");
        trow.setAttribute("class", "");
    }

    function setUnselectedFromFindID(find_id){
        //  Takes a find_id (eg find6) and unselects that find
        var trow_id = "tablerow_".concat(find_id)
        var trow = document.getElementById(trow_id);
        var this_find = document.getElementById(find_id);
        this_find.setAttribute("class", "find");
        trow.setAttribute("class", "");
    }

    function setUnselectedFromFieldID(field_id){
        //  Takes a field (eg field6) and unselects that field
        var trow_id = "tablerow_".concat(field_id)
        var trow = document.getElementById(trow_id);
        var this_field = document.getElementById(field_id);
        this_field.setAttribute("class", "field");
        trow.setAttribute("class", "hidden");
    }

    function toggleFieldHighlight(field_id){

        //  Takes a field_id as an argument - if the field is selected, it unselects
        //  If the field is unselected, it will select it.  This is done by changing
        //  the classes between "field" and "field_selected" as necessary

        field = document.getElementById(field_id)
        if (field.getAttribute("class") == "field_selected") {
            field.setAttribute("class", "field");
        } else {
            field.setAttribute("class", "field_selected");
        }
    }


    function toggleFindHighlight(find_id){

        //  Takes a find_id as an argument - if the find is selected, it unselects
        //  If the find is unselected, it will select it.  This is done by changing
        //  the classes between "find" and "find_selected" as necessary

        find = document.getElementById(find_id)
        if (find.getAttribute("class") == "find_selected") {
            find.setAttribute("class", "find");
        } else {
            find.setAttribute("class", "find_selected");
        }
    }

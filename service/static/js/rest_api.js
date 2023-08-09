$(function () {

    // Update the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_name").val(res.name);
        $("#promotion_start_date").val(res.start_date);
        $("#promotion_end_date").val(res.end_date);
        if (res.whole_store == true) {
            $("#promotion_whole_store").val("true");
        } else {
            $("#promotion_whole_store").val("false");
        }
        if (res.has_been_extended == true) {
            $("#promotion_has_been_extended").val("true");
        } else {
            $("#promotion_has_been_extended").val("false");
        }
        $("#promotion_original_end_date").val(res.original_end_date);
        $("#promotion_message").val(res.message);
        if (res.promotion_changes_price == true) {
            $("#promotion_changes_price").val("true");
        } else {
            $("#promotion_changes_price").val("false");
        }
    }

    // Clears all form fields
    function clear_form_data() {
        $("#promotion_name").val("");
        $("#promotion_start_date").val("");
        $("#promotion_end_date").val("");
        $("#promotion_whole_store").val("");
        $("#promotion_has_been_extended").val("");
        $("#promotion_original_end_date").val("");
        $("#promotion_changes_price").val("");
    }
    
    // Update flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // List Promotions
    // ****************************************

    $("#list-btn").click(function () {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: "/promotions",
            contentType: "application/json",
	        data: ''
        });
        ajax.done(function(res){
            console.log(res)
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Start Date</th>'
            table += '<th class="col-md-2">End Date</th>'
            table += '<th class="col-md-2">Whole Store</th>'
            table += '<th class="col-md-2">Has Been Extended</th>'
            table += '<th class="col-md-2">Original End Date</th>'
            table += '<th class="col-md-2">Message</th>'
            table += '<th class="col-md-2">Promotion Changes Price</th>'
            table += '</tr></thead><tbody>'

            let firstPromo = "";
            for(let i = 0; i < res.length; i++) {
                let promo = res[i];
                table +=  `<tr id="row_${i}"><td>${promo.id}</td><td>${promo.name}</td><td>${promo.start_date}</td><td>${promo.end_date}</td><td>${promo.whole_store}</td><td>${promo.has_been_extended}</td><td>${promo.original_end_date}</td><td>${promo.message}</td><td>${promo.promotion_changes_price}</td></tr>`;
                if (i == 0) {
                    firstPromo = promo;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);
	        if (firstPromo != "") {
                update_form_data(firstPromo)
            }
            flash_message("Success")
        });
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#promotion_name").val();
        let message = $("#promotion_message").val();
        let start_date = $("#promotion_start_date").val();
        let end_date = $("#promotion_end_date").val();

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (message) {
            if (queryString.length > 0) {
                queryString += '&message=' + message
            } else {
                queryString += 'message=' + message
            }
        }
        if (start_date) {
            if (queryString.length > 0) {
                queryString += '&start_date=' + available
            } else {
                queryString += 'start_date=' + available
            }
        }

        if (end_date) {
            if (queryString.length > 0) {
                queryString += '&end_date=' + available
            } else {
                queryString += 'end_date=' + available
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            console.log(res);
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Start Date</th>'
            table += '<th class="col-md-2">End Date</th>'
            table += '<th class="col-md-2">Whole Store</th>'
            table += '<th class="col-md-2">Has Been Extended</th>'
            table += '<th class="col-md-2">Original End Date</th>'
            table += '<th class="col-md-2">Message</th>'
            table += '<th class="col-md-2">Promotion Changes Price</th>'

            table += '</tr></thead><tbody>'


            let firstPromo = "";
            for(let i = 0; i < res.length; i++) {
                let promo = res[i];
                table +=  `<tr id="row_${i}"><td>${promo.id}</td><td>${promo.name}</td><td>${promo.start_date}</td><td>${promo.end_date}</td><td>${promo.whole_store}</td><td>${promo.has_been_extended}</td><td>${promo.original_end_date}</td><td>${promo.message}</td><td>${promo.changes_price}</td></tr>`;
                if (i == 0) {
                    firstPromo = promo;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPromo != "") {
                update_form_data(firstPromo)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Cancel a Promotion
    // ****************************************

    $("#cancel-btn").click(function () {

        let id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions/cancel/${id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            console.log("cancel", res);

            flash_message(`Promotion canceled!`)
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });  

    // ****************************************
    // Delete a Promotion
    // ****************************************  

    $("#delete-btn").click(function(){

        let id = $("#promotion_id").val();
        
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/promotions/${id}`,
            contentType: "application/json",
            data: '',
        })
        ajax.done(function(res){
            clear_form_data()
            flash_message("Promotion has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });
})

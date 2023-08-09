$(function () {
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_name").val(res.name);
        $("#promotion_message").val(res.message);
        if (res.whole_store == true) {
            $("#promotion_whole_store").val("True");
        } else {
            $("#promotion_whole_store").val("False");
        }
        if (res.promotion_changes_price == true) {
            $("#promotion_promotion_changes_pricee").val("True");
        } else {
            $("#promotion_promotion_changes_price").val("False");
        }

        let start_date = new Date(res.start_date);
        let month = start_date.getUTCMonth() + 1; //months from 1-12
        let day = start_date.getUTCDate();
        let year = start_date.getUTCFullYear();

        if(day.toString().length === 1){
            day = `0${day}`
        }

        if(month.toString().length === 1){
            month = `0${month}`
        }
        
        start_date = year + "-" + month + "-" + day;
        console.log(start_date)
        let end_date = new Date(res.end_date);
        month = end_date.getUTCMonth() + 1; //months from 1-12
        day = end_date.getUTCDate();
        year = end_date.getUTCFullYear();

        if(day.toString().length === 1){
            day = `0${day}`
        }

        if(month.toString().length === 1){
            month = `0${month}`
        }

        end_date = year + "-" + month + "-" + day;

        $("#promotion_start_date").val(start_date);
        $("#promotion_end_date").val(end_date);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_name").val("");
        $("#promotion_message").val("");
        $("#promotion_start_date").val("");
        $("#promotion_end_date").val("");
        $("#promotion_whole_store").val("");
        $("#promotion_changes_price").val("");
    }

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    $("#create-btn").click(function () {

        let id = $("#promotion_name").val();
        let name = $("#promotion_name").val();
        let message = $("#promotion_message").val();
        let start_date = $("#promotion_start_date").val();
        let end_date = $("#promotion_end_date").val();
        let whole_store = $("#promotion_whole_store").val();
        let promotion_changes_price = $("#promotion_promotion_changes_price").val();

        let data = {
            "name": name,
            "message": message,
            "start_date": start_date,
            "end_date": end_date,
            "whole_store": whole_store,
            "promotion_changes_price": promotion_changes_price,
            "has_been_extended": "False",
            "original_end_date": end_date
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

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
                queryString += '&start_date=' + start_date
            } else {
                queryString += 'start_date=' + start_date
            }
        }

        if (end_date) {
            if (queryString.length > 0) {
                queryString += '&end_date=' + end_date
            } else {
                queryString += 'end_date=' + end_date
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
})



function fill_div_part(div_id, path, parameters = {}) {
    var div_part = document.getElementById(div_id);

    console.log("Filling DIV Part: " + div_id + ', path: ' + path + ', paramters: ' + JSON.stringify(parameters));
    $.ajax({
        type: "get",
        url: path,
        data: parameters,
        success: function(response) {
            console.log("Success DIV Part: " + div_id + ', path: ' + path + ', paramters: ' + JSON.stringify(parameters));
            div_part.innerHTML = response;
        },
        error: function(response) {
            console.log("FAILURE DIV Part: " + div_id + ', path: ' + path + ', paramters: ' + JSON.stringify(parameters) + ', error: ' + response.status);
            testOutputBox.value = "FAILURE";
        }
    });

}
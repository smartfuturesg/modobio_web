function add_signature_pad(canvas_id, form_id, clear_button_id, signature_field_id) {
    var canvas = document.getElementById(canvas_id);
    var form = document.getElementById(form_id);
    var clear  = document.getElementById(clear_button_id);
    var sigbox = document.getElementById(signature_field_id);
    var pad = new SignaturePad(canvas);

    var ratio =  Math.max(window.devicePixelRatio || 1, 1);
    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = canvas.offsetHeight * ratio;
    canvas.getContext("2d").scale(ratio, ratio);

    if (sigbox.value != "") {
        pad.fromDataURL(sigbox.value);
    }

    form.onsubmit = function() {
        if (pad.isEmpty()) {
            alert("Please sign the document before clicking Accept.");
            return false
        } else {
            sigbox.value = pad.toDataURL();
        }
    }

    clear.addEventListener("click", function() {
        pad.clear();
    });
}

function age(birthday) {
    var now = new Date();
    var bday = new Date(birthday);
    // Born in the future
    if (now <= bday) {
        return 0
    }
    var age_diff = now - bday.getTime();                // in millisec
    var age_date = new Date(age_diff);                  // millisec from epoch
    return Math.abs(age_date.getUTCFullYear() - 1970);
}

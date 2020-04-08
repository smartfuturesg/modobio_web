function add_signature_pad(submit_button, signature_field) {
    var canvas = document.querySelector("canvas");
    var pad = new SignaturePad(canvas);
    var submit = document.getElementById(submit_button);
    var sigbox = document.getElementById(signature_field);
    submit.addEventListener("click", function() {
        if (pad.isEmpty()) {
            alert("Please sign the document before clicking Accept.");
            return false
        } else {
            sigbox.value = pad.toDataURL();
        }
    })
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

function toggle(target_class, id) {
    var divs = document.querySelectorAll(target_class);
    divs.forEach(div => {
        if (div.id == id && div.style.display == "none") {
            div.style.display = "inline-block";
        } else {
            div.style.display = "none";
        }
    });
};

function add_toggles(listen_class, target_class) {
    var divs = document.querySelectorAll(listen_class);
    divs.forEach(div => {
        div.addEventListener("click", function(){
            var target_id = this.getAttribute('data-id');
            toggle(target_class, target_id);
        });
    });
};

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
    if (now < bday) {
        return 0
    }
    var age_diff = now - bday.getTime();                // in millisec
    var age_date = new Date(age_diff);                  // milisec from epoch
    return Math.abs(age_date.getUTCFullYear() - 1970);
}

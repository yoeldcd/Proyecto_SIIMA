

function switchPasswordVisibility(inputid, targetid) {
    let btimg = $(`#${targetid}`)[0];
    let input = $(`#${inputid}`)[0];
    
    // change password visibility and button logo
    input.type = (input.type == 'password') ? 'text' : input.type = 'password';
    btimg.src = (input.type == 'text') ? '/static/img/hide-dark.svg' : '/static/img/see-dark.svg';

}

function mathInputs(input1id, input2id) {
    let input1 = $(`#${input1id}`)[0];
    let input2 = $(`#${input2id}`)[0];
    
    // enfatize input with succes or error color
    if (input1.value != '' || input2.value != '') {
        input2.style.cssText = (input2.value != input1.value) ? 'background: #ef9a96' : 'background: #49f3ac';
        return;
    }
    
    input2.style.cssText = 'background: inherited';
};

function mathType(ke, inputid, type) {
    
    let input1 = $(`#${inputid}`)[0];
    let math = false;
    
    // acept only characters of ASCII type range
    switch (type) {
        case 'number-only':
            return ke.charCode >= 48 && ke.charCode <= 57;
            
        case 'text-only':
            return ke.charCode < 48 && ke.charCode > 57;
    
    }
    
    return true;
}

function verifyEmail(inputid){    
    let input = $(`#${inputid}`)[0];
    let isEmail = input.value.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$");
    
    if (input.value.length > 0 && !isEmail){
        // apply error field style
        input.style.border = 'solid 2px red';
        return;
    }
    
    // apply default field style
    input.style.border = 'none';
    input.style.borderBottom = 'solid 2px #2fb166';
    
}

function clickElement(id) {
    $(`#${id}`).click();
}


function switchPasswordVisibility(inputid, targetid) {
    let btimg = document.getElementById(targetid);
    let input = document.getElementById(inputid);

    // change password visibility and button logo
    input.type = (input.type == 'password') ? 'text' : input.type = 'password';
    btimg.src = (input.type == 'text') ? './img/eye-slash-fill.svg' : './img/eye-fill.svg';

}

function mathInputs(input1id, input2id) {
    let input1 = document.getElementById(input1id);
    let input2 = document.getElementById(input2id);
    
    // enfatize input with succes or error color
    if(input1.value != '' || input2.value != ''){
        input2.style.cssText = (input2.value != input1.value) ? 'background: #ef9a96' : 'background: #49f3ac';
        return;
    }
    
    input2.style.cssText = 'background: white';
};

function clickElement(id){
    document.getElementById(id).click();
}
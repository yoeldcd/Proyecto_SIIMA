
addEventListener('load', setEditListeners);

function setEditListeners(){
    
    // subscribe all button to eventlistener of click
    for (let e of $('.edit-button'))
        e.addEventListener('click', loadItem)
}

function loadItem(e){
    let index = this.getAttribute('index');
    let test = tests[index];
    
    console.log(index);
    
    // store values
    document.getElementById('test_type').innerText = test.type;
    document.getElementById('test_patient_CI').innerText = test.patientCI;
    document.getElementById('test_ID').innerText = test.id;
    
}


addEventListener('load', setItemsListeners);

function setItemsListeners(){
    
    // subscribe all button to eventlistener of click
    for (let e of $('.edit-test-button'))
        e.addEventListener('click', loadTestItem)
}

function loadTestItem(e){
    let index = this.getAttribute('index');
    let test = tests[index];
    
    console.log(index);
    
    // store values
    $('#test_type')[0].value = test.type;
    $('#test_patient_CI')[0].value = test.patientCI;
    $('#test_ID')[0].value = test.test_id;
    $('#test_result')[0].value = test.result;
    
    $('#resolve_test_form')[0].action = '/test/resolve/'+test.id
    
}

function notifyItem(){
    let request = new XMLHttpRequest();
    request.url = 'tests/notify/';


}

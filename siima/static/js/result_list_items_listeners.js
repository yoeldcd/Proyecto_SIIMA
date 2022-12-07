
addEventListener('load', setItemsListeners);

function setItemsListeners(){
    
    // subscribe all button to eventlistener of click
    for (let e of $('.detail-test-button'))
        e.addEventListener('click', loadTestItem)
}

function loadTestItem(e){
    let index = this.getAttribute('index');
    let test = tests[index];
    
    console.log(index);
    
    // store values
    $('#detailed_test_type').text(test.type);
    $('#detailed_test_result').text(test.result);
    $('#detailed_test_begin_date').text(test.begin_date);
    $('#detailed_test_resolution_date').text(test.resolution_date);
    
    $('#detailed_test_supress_link')[0].href = '/result/supress/'+test.id
    
}

function notifyItem(){
    let request = new XMLHttpRequest();
    request.url = 'tests/notify/';


}

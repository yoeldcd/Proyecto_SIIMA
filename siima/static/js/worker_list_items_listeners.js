
addEventListener('load', setItemsListeners);

function setItemsListeners(){
    
    // subscribe all button to eventlistener of click
    for (let e of $('.detail-worker-button'))
        e.addEventListener('click', loadPatientItem)
}

function loadPatientItem(e){
    let index = this.getAttribute('index');
    let worker = workers[index];
    
    console.log(index);
    
    // store values
    $('#detailed_worker_icon')[0].src = "/static/img/profiles/"+worker.icon_path;
    
    $('#detailed_worker_system_role').text(worker.system_role);
    $('#detailed_worker_username').text(worker.username);
    $('#detailed_worker_ci').text(worker.ci);
    
    $('#detailed_worker_first_name').text(worker.first_name);
    $('#detailed_worker_last_name').text(worker.last_name);
    $('#detailed_worker_age').text(worker.age);
    $('#detailed_worker_sex').text(worker.sex);
    $('#detailed_worker_role').text(worker.role);
    
    if($('#detailed_worker_actions'))
        $('#detailed_worker_actions').text(worker.actions);
    
    $('#detailed_worker_last_login').text(worker.last_login);
    $('#detailed_worker_date_joined').text(worker.date_joined);
    
    if($('#detailed_worker_events_link')[0])
        $('#detailed_worker_events_link')[0].href = '/events/?user_id='+worker.id;
    
    if($('#detailed_worker_edit_link')[0])
        $('#detailed_worker_edit_link')[0].href = '/worker/edit/'+worker.id;
    
    if($('#detailed_worker_supress_link')[0])
        $('#detailed_worker_supress_link')[0].href = '/worker/supress/'+worker.id;
    
}


addEventListener('load', setItemsListeners);

function setItemsListeners(){
    
    // subscribe all button to eventlistener of click
    for (let e of $('.detail-patient-button'))
        e.addEventListener('click', loadPatientItem)
}

function loadPatientItem(e){
    let index = this.getAttribute('index');
    let patient = patients[index];
    
    console.log(index);
    
    // store values
    $('#detailed_patient_icon')[0].src = "/static/img/profiles/"+patient.icon_path;
    
    $('#detailed_patient_username').text(patient.username);
    $('#detailed_patient_first_name').text(patient.first_name);
    $('#detailed_patient_last_name').text(patient.last_name);
    $('#detailed_patient_age').text(patient.age);
    $('#detailed_patient_sex').text(patient.sex);
    $('#detailed_patient_last_login').text(patient.last_login);
    $('#detailed_patient_date_joined').text(patient.date_joined);
    
    $('#detailed_patient_events_link')[0].href = '/events/?user_id='+patient.id;
    $('#detailed_patient_edit_link')[0].href = '/patient/edit/'+patient.id;
    $('#detailed_patient_supress_link')[0].href = '/patient/supress/'+patient.id;
    
}

function notifyItem(){
    let request = new XMLHttpRequest();
    request.url = 'tests/notify/';
}

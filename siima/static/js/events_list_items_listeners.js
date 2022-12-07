
addEventListener('load', setItemsListeners);

function setItemsListeners() {

    // subscribe all button to eventlistener of click
    for (let e of $('.detail-event-button'))
        e.addEventListener('click', loadEventItem)
}

function loadEventItem(e) {
    let index = this.getAttribute('index');
    let event = events[index];

    console.log(index);

    // store values

    $('#detailed_event_type').text(event.type);

    // Select event type color
    
    switch (event.type) {
        case 'danger':
            $('#detailed_event_type')[0].style.backgroundColor = 'red'
            $('#detailed_event_type')[0].style.color = 'white'
            break;
        
        case 'warning':
            $('#detailed_event_type')[0].style.backgroundColor = 'yellow'
            $('#detailed_event_type')[0].style.color = 'black'
            break;
        
        default:
            $('#detailed_event_type')[0].style.backgroundColor = 'inherited'
            $('#detailed_event_type')[0].style.color = 'black'
    }
    
    $('#detailed_event_title').text(event.title);
    $('#detailed_event_message').text(event.message);
    $('#detailed_event_date').text(event.date);

    $('#detailed_event_supress_link')[0].href = '/event/supress/' + event.id;

}

function notifyItem() {
    let request = new XMLHttpRequest();
    request.url = 'tests/notify/';
}

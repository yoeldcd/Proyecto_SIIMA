
function showMessage(type, title, message) {
    
    // set message layout style class
    $('#genericMessage').removeClass();
    $('#genericMessage').addClass('alert');
    $('#genericMessage').addClass(`alert-${type}`);
    
    // set message content
    $('#genericMessageTitle').text(title ? new String(title) : "")
    $('#genericMessageDescription').text(message ? new String(message) : "")
    
    // show message layout dialog
    $('#genericMessageDialog').modal('show')

}

// typed message action functions
function showErrorMessage(ttl, msg) { showMessage('danger', ttl, msg) }

function showLogMessage(ttl, msg) { showMessage('primary', ttl, msg) }

function showSuccessMessage(ttl, msg) { showMessage('success', ttl, msg) }

function showWarningMessage(ttl, msg) { showMessage('warning', ttl, msg) }

function showQueryMessage(qmsg) {

    let content = qmsg.split(', ')

    // select and show query message dialog
    switch (content[0].toUpperCase()) {
        case 'ERROR':
            showErrorMessage(content[1], content[2])
            break;
        case 'WARNING':
            showWarningMessage(content[1], content[2])
            break;
        case 'NOTICE':
            showLogMessage(content[1], content[2])
            break;

        default:
            showSuccessMessage(content[1], content[2])
    }

}

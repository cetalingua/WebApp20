var el = x => document.getElementById(x);

function showPicker(inputId) { el('file-input').click(); }

function showPicked(input) {
    el('upload-label').innerHTML = input.files[0].name;
    var reader = new FileReader();
    reader.onload = function (e) {
        el('image-picked').src = e.target.result;
        el('image-picked').className = '';
    }
    reader.readAsDataURL(input.files[0]);
}

function analyze() {
    var uploadFiles = el('file-input').files;

    if (uploadFiles.length != 1) {
        alert('Please select 1 file to analyze');
        return;
    }

    el('analyze-button').innerHTML = 'Analyzing...';
    var xhr = new XMLHttpRequest();
    var loc = window.location;
    xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`, true);
    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
            var response = JSON.parse(e.target.responseText);
            el('result-label').innerHTML = `Result = ${response['result']}`;
        }
        el('analyze-button').innerHTML = 'Analyze';
    }

    var fileData = new FormData();
    fileData.append('file', uploadFiles[0]);
    xhr.send(fileData);
}

function fetch_analyze() {
    var imageUrl = el('image_url').value;

    if (imageUrl.trim().length == 0) {
        alert('Please set the url to image you want to analyze');
        return;
    }

    el('analyze-button').innerHTML = 'Fetching and Analyzing...';
    var xhr = new XMLHttpRequest();
    var loc = window.location;

    xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/fetch_analyze`, true);
    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
            var response = JSON.parse(e.target.responseText);
            el('result-label').innerHTML = `Result = ${response['result']}`;
            el('image-picked').src = "data:image/jpg;base64,"+response['img_b64'];
            el('image-picked').className = '';
        }
        el('analyze-button').innerHTML = 'Analyze';
    }


    var fileData = new FormData();
    fileData.append('url', imageUrl);
    xhr.send(fileData);
}

function select_random_image() {    
    el('select-random-image-button').innerHTML = 'Analyzing...';
    var xhr = new XMLHttpRequest();
    var loc = window.location;

    xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/select_random_image`, true);
    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
            var response = JSON.parse(e.target.responseText);
            el('result-label').innerHTML = `Result = ${response['result']}`;
            el('image-picked').src = "data:image/jpg;base64,"+response['img_b64'];
            el('image-picked').className = '';
            el('select-random-image-button').innerHTML = 'Select Random Image';
        }
        el('analyze-button').innerHTML = 'Analyze';
    }


    //var fileData = new FormData();
    //fileData.append('url', imageUrl);
    xhr.send();//fileData);
}

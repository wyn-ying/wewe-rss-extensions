function updateAdditionalInputs(cls) {
    const additionalInputsContainer = document.getElementById('additional-inputs');

    additionalInputsContainer.innerHTML = '';
    const optionalLabel = document.createElement('optionalLabel');
    optionalLabel.type = 'label';
    optionalLabel.textContent = 'Notifier必填项: ';
    additionalInputsContainer.appendChild(optionalLabel);
    if (cls === 'FeishuNotifier') {
        const fsTokenInput = document.createElement('input');
        fsTokenInput.type = 'text';
        fsTokenInput.name = 'fs_token';
        fsTokenInput.placeholder = 'Feishu Token';
        fsTokenInput.required = true;
        additionalInputsContainer.appendChild(fsTokenInput);
    } else if (cls === 'DingtalkNotifier') {
        const accessTokenInput = document.createElement('input');
        accessTokenInput.type = 'text';
        accessTokenInput.name = 'access_token';
        accessTokenInput.placeholder = 'Access Token';
        accessTokenInput.required = true;
        additionalInputsContainer.appendChild(accessTokenInput);

        const secretInput = document.createElement('input');
        secretInput.type = 'text';
        secretInput.name = 'secret';
        secretInput.placeholder = 'Secret';
        secretInput.required = true;
        additionalInputsContainer.appendChild(secretInput);
    }
}

function showEditDefaultInverval(index, cls) {
    document.querySelectorAll('[id^="edit-form-"]').forEach(function(editForm) {
        if (editForm.id != 'edit-form-interval') {
            editForm.style.display = 'none';
        }
    });

    const container = document.getElementById('edit-inputs-interval');
    container.innerHTML = '';
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'default_interval_minutes';
    input.placeholder = 'Default Interval Minutes(240 as default)';
    input.style = 'width: 240px;';
    input.required = true;
    container.appendChild(input);
    document.getElementById('edit-form-interval').style.display = 'block';
}

function submitEditDefaultInverval() {
    const inputsContainer = document.getElementById('edit-inputs-interval');
    const formData = new FormData();
    const input = inputsContainer.querySelector('input');
    formData.append(input.name, input.value);
    fetch('/base/edit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        console.log(data);
        document.getElementById('edit-form-interval').style.display = 'none';
    })
    .catch(error => console.error('Error:', error));

    window.location.reload();
}

function cancelEditDefaultInverval() {
    document.getElementById('edit-form-interval').style.display = 'none';
    window.location.reload();
}

function generateNotifierInputs(cls, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'interval_minutes';
    input.placeholder = 'Interval Minutes(240 as default)';
    input.style = 'width: 200px;';
    input.required = false;
    container.appendChild(input);
    if (cls === 'FeishuNotifier') {
        const fsTokenInput = document.createElement('input');
        fsTokenInput.type = 'text';
        fsTokenInput.name = 'fs_token';
        fsTokenInput.placeholder = 'Feishu Token';
        container.appendChild(fsTokenInput);

    }
    else if (cls === 'DingtalkNotifier') {
        const accessTokenInput = document.createElement('input');
        accessTokenInput.type = 'text';
        accessTokenInput.name = 'access_token';
        accessTokenInput.placeholder = 'Access Token';
        container.appendChild(accessTokenInput);

        const secretInput = document.createElement('input');
        secretInput.type = 'text';
        secretInput.name = 'secret';
        secretInput.placeholder = 'Secret';
        container.appendChild(secretInput);
    }
}

function showEditNotifier(index, cls) {
    document.querySelectorAll('[id^="edit-form-"]').forEach(function(editForm) {
        if (editForm.id != 'edit-form-' + index) {
            editForm.style.display = 'none';
        }
    });

    const editContainerId = 'edit-inputs-' + index;
    generateNotifierInputs(cls, editContainerId);
    document.getElementById('edit-form-' + index).style.display = 'block';
}

function submitEditNotifier(index) {
    const inputsContainer = document.getElementById('edit-inputs-' + index);
    const formData = new FormData();
    formData.append('idx', index);
    inputsContainer.querySelectorAll('input').forEach(input => {
        formData.append(input.name, input.value);
    });
    fetch('/notifier/edit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        console.log(data);
        document.getElementById('edit-form-' + index).style.display = 'none';
    })
    .catch(error => console.error('Error:', error));

    window.location.reload();
}

function cancelEditNotifier(index) {
    document.getElementById('edit-form-' + index).style.display = 'none';
    window.location.reload();
}

// 页面加载时，初始化下拉菜单的监听器
document.addEventListener('DOMContentLoaded', function() {
    const clsSelect = document.getElementById('notifier-class');
    const defaultCls = clsSelect.options[clsSelect.selectedIndex].value; // 获取默认选中的 cls 值
    updateAdditionalInputs(defaultCls); // 根据默认选中的 cls 值更新输入框

    // 为下拉菜单添加事件监听器
    clsSelect.addEventListener('change', function() {
        updateAdditionalInputs(this.value);
    });
});
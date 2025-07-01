document.addEventListener('DOMContentLoaded', function() {
    const departmentSelect = document.getElementById('department-select');
    const dteSelect = document.getElementById('dte-select');
    const updateBtn = document.getElementById('update-org-info-btn');
    const updateStatus = document.getElementById('update-status');

    function fetchDTEs(departmentId, selectedDteId) {
        if (!departmentId) {
            dteSelect.innerHTML = '<option value="">DTEを選択</option>';
            return;
        }
        fetch(`/departments/api/departments/${departmentId}/dtes/`)
            .then(response => response.json())
            .then(data => {
                dteSelect.innerHTML = '<option value="">DTEを選択</option>';
                data.forEach(dte => {
                    const option = document.createElement('option');
                    option.value = dte.id;
                    option.textContent = dte.name;
                    if (selectedDteId && dte.id == selectedDteId) {
                        option.selected = true;
                    }
                    dteSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching DTEs:', error);
            });
    }

    departmentSelect.addEventListener('change', function() {
        fetchDTEs(this.value, null);
    });

    updateBtn.addEventListener('click', function() {
        updateBtn.disabled = true;
        updateBtn.innerHTML = '<svg class="animate-spin mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>更新中...';
        
        const departmentId = departmentSelect.value;
        const dteId = dteSelect.value;
        const employeeId = "{{ profile.user.pk }}";

        fetch(`/profiles/update-org-info/${employeeId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ department_id: departmentId, dte_id: dteId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateStatus.innerHTML = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"><svg class="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 8 8"><circle cx="4" cy="4" r="3"/></svg>' + data.message + '</span>';
                document.getElementById('user-org-info-container').innerHTML = data.html;
                setTimeout(() => {
                    updateStatus.innerHTML = '';
                }, 3000);
            } else {
                updateStatus.innerHTML = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"><svg class="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 8 8"><circle cx="4" cy="4" r="3"/></svg>' + data.message + '</span>';
            }
        })
        .catch(error => {
            updateStatus.innerHTML = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">エラーが発生しました</span>';
        })
        .finally(() => {
            updateBtn.disabled = false;
            updateBtn.innerHTML = '<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>更新';
        });
    });

    // Initial fetch for DTEs on page load
    const initialDepartmentId = departmentSelect.value;
    const initialDteId = "{{ profile.user.dte.id|default:'' }}";
    if(initialDepartmentId){
        fetchDTEs(initialDepartmentId, initialDteId);
    }

    // ML更新処理
    const mlSelect = document.getElementById('ml-select');
    const updateMlBtn = document.getElementById('update-ml-btn');
    const updateMlStatus = document.getElementById('update-ml-status');
    const employeeId = document.querySelector('[data-employee-id]').dataset.employeeId;
    const csrfToken = document.querySelector('[data-csrf-token]').dataset.csrfToken;

    if (updateMlBtn) {
        updateMlBtn.addEventListener('click', function() {
            updateMlBtn.disabled = true;
            updateMlBtn.innerHTML = '<svg class="animate-spin mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>更新中...';

            const mlValue = mlSelect.value;

            fetch(`/employees/update-ml/${employeeId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `ml=${mlValue}`
            })
            .then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    return response.text().then(text => {
                        throw new Error(text);
                    });
                }
            })
            .then(message => {
                updateMlStatus.innerHTML = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"><svg class="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 8 8"><circle cx="4" cy="4" r="3"/></svg>' + message + '</span>';
                setTimeout(() => {
                    location.reload();
                }, 1000);
            })
            .catch(error => {
                console.error('Error updating ML:', error);
                updateMlStatus.innerHTML = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">' + error.message + '</span>';
            })
            .finally(() => {
                updateMlBtn.disabled = false;
                updateMlBtn.innerHTML = '<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>更新';
            });
        });
    }
});
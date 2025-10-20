document.addEventListener('DOMContentLoaded', function() {
    const stateSelect = document.getElementById('state');
    const districtSelect = document.getElementById('district');
    const complexSelect = document.getElementById('complex');
    const courtSelect = document.getElementById('court');
    const dateInput = document.getElementById('date');
    const downloadAllBtn = document.getElementById('downloadAllBtn');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');

    const lookupStateSelect = document.getElementById('lookupState');
    const lookupDistrictSelect = document.getElementById('lookupDistrict');
    const lookupLoading = document.getElementById('lookupLoading');
    const lookupResult = document.getElementById('lookupResult');

    dateInput.valueAsDate = new Date();

    loadStates();
    loadStatesForLookup();

    function showLoading(loadingElement) {
        loadingElement.style.display = 'block';
    }

    function hideLoading(loadingElement) {
        loadingElement.style.display = 'none';
    }

    function showResult(resultElement, message, type = 'success') {
        resultElement.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }

    async function loadStates() {
        try {
            const response = await fetch('/api/get-states');
            const data = await response.json();

            if (data.success) {
                stateSelect.innerHTML = '<option value="">Select State</option>';
                data.states.forEach(state => {
                    const option = document.createElement('option');
                    option.value = state.value;
                    option.textContent = state.text;
                    stateSelect.appendChild(option);
                });
            } else {
                showResult(result, `Error: ${data.error}`, 'danger');
            }
        } catch (error) {
            showResult(result, `Error loading states: ${error.message}`, 'danger');
        }
    }

    async function loadStatesForLookup() {
        try {
            const response = await fetch('/api/get-states');
            const data = await response.json();

            if (data.success) {
                lookupStateSelect.innerHTML = '<option value="">Select State</option>';
                data.states.forEach(state => {
                    const option = document.createElement('option');
                    option.value = state.value;
                    option.textContent = state.text;
                    lookupStateSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading states for lookup:', error);
        }
    }

    stateSelect.addEventListener('change', async function() {
        const stateCode = this.value;

        districtSelect.innerHTML = '<option value="">Select District</option>';
        complexSelect.innerHTML = '<option value="">Select Court Complex</option>';
        courtSelect.innerHTML = '<option value="">Select Court (Optional)</option>';

        districtSelect.disabled = true;
        complexSelect.disabled = true;
        courtSelect.disabled = true;
        downloadAllBtn.disabled = true;

        if (!stateCode) return;

        showLoading(loading);

        try {
            const response = await fetch('/api/get-districts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ state_code: stateCode })
            });

            const data = await response.json();
            hideLoading(loading);

            if (data.success) {
                data.districts.forEach(district => {
                    const option = document.createElement('option');
                    option.value = district.value;
                    option.textContent = district.text;
                    districtSelect.appendChild(option);
                });
                districtSelect.disabled = false;
            } else {
                showResult(result, `Error: ${data.error}`, 'danger');
            }
        } catch (error) {
            hideLoading(loading);
            showResult(result, `Error loading districts: ${error.message}`, 'danger');
        }
    });

    districtSelect.addEventListener('change', async function() {
        const stateCode = stateSelect.value;
        const districtCode = this.value;

        complexSelect.innerHTML = '<option value="">Select Court Complex</option>';
        courtSelect.innerHTML = '<option value="">Select Court (Optional)</option>';

        complexSelect.disabled = true;
        courtSelect.disabled = true;
        downloadAllBtn.disabled = true;

        if (!districtCode) return;

        showLoading(loading);

        try {
            const response = await fetch('/api/get-court-complexes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ state_code: stateCode, district_code: districtCode })
            });

            const data = await response.json();
            hideLoading(loading);

            if (data.success) {
                data.complexes.forEach(complex => {
                    const option = document.createElement('option');
                    option.value = complex.value;
                    option.textContent = complex.text;
                    complexSelect.appendChild(option);
                });
                complexSelect.disabled = false;
            } else {
                showResult(result, `Error: ${data.error}`, 'danger');
            }
        } catch (error) {
            hideLoading(loading);
            showResult(result, `Error loading court complexes: ${error.message}`, 'danger');
        }
    });

    complexSelect.addEventListener('change', async function() {
        const stateCode = stateSelect.value;
        const districtCode = districtSelect.value;
        const complexCode = this.value;

        courtSelect.innerHTML = '<option value="">Select Court (Optional)</option>';
        courtSelect.disabled = true;
        downloadAllBtn.disabled = true;

        if (!complexCode) return;

        showLoading(loading);

        try {
            const response = await fetch('/api/get-courts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    state_code: stateCode, 
                    district_code: districtCode,
                    complex_code: complexCode
                })
            });

            const data = await response.json();
            hideLoading(loading);

            if (data.success) {
                data.courts.forEach(court => {
                    const option = document.createElement('option');
                    option.value = court.value;
                    option.textContent = court.text;
                    courtSelect.appendChild(option);
                });
                courtSelect.disabled = false;
                downloadAllBtn.disabled = false;
            } else {
                showResult(result, `Error: ${data.error}`, 'danger');
            }
        } catch (error) {
            hideLoading(loading);
            showResult(result, `Error loading courts: ${error.message}`, 'danger');
        }
    });

    lookupStateSelect.addEventListener('change', async function() {
        const stateCode = this.value;

        lookupDistrictSelect.innerHTML = '<option value="">Select District</option>';
        lookupDistrictSelect.disabled = true;

        if (!stateCode) return;

        showLoading(lookupLoading);

        try {
            const response = await fetch('/api/get-districts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ state_code: stateCode })
            });

            const data = await response.json();
            hideLoading(lookupLoading);

            if (data.success) {
                data.districts.forEach(district => {
                    const option = document.createElement('option');
                    option.value = district.value;
                    option.textContent = district.text;
                    lookupDistrictSelect.appendChild(option);
                });
                lookupDistrictSelect.disabled = false;
            } else {
                showResult(lookupResult, `Error: ${data.error}`, 'danger');
            }
        } catch (error) {
            hideLoading(lookupLoading);
            showResult(lookupResult, `Error loading districts: ${error.message}`, 'danger');
        }
    });

    document.getElementById('causelistForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const stateCode = stateSelect.value;
        const districtCode = districtSelect.value;
        const complexCode = complexSelect.value;
        const courtCode = courtSelect.value;
        const date = dateInput.value;

        if (!stateCode || !districtCode || !complexCode || !courtCode) {
            showResult(result, 'Please select all required fields including a court', 'warning');
            return;
        }

        const formattedDate = new Date(date).toLocaleDateString('en-GB').replace(/\//g, '/');

        showLoading(loading);
        result.innerHTML = '';

        try {
            const response = await fetch('/api/download-causelist', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    state_code: stateCode,
                    district_code: districtCode,
                    complex_code: complexCode,
                    court_code: courtCode,
                    date: formattedDate
                })
            });

            const data = await response.json();
            hideLoading(loading);

            if (data.success) {
                showResult(result, `
                    <i class="fas fa-check-circle"></i> <strong>Success!</strong><br>
                    ${data.message}<br>
                    <strong>File:</strong> ${data.filename}<br>
                    <strong>Cases Found:</strong> ${data.cases_found}<br>
                    <a href="/api/download-file/${data.filename}" class="btn btn-primary btn-sm mt-2" download>
                        <i class="fas fa-download"></i> Download PDF
                    </a>
                `, 'success');
            } else {
                showResult(result, `<i class="fas fa-exclamation-triangle"></i> Error: ${data.error}`, 'danger');
            }
        } catch (error) {
            hideLoading(loading);
            showResult(result, `<i class="fas fa-exclamation-triangle"></i> Error: ${error.message}`, 'danger');
        }
    });

    downloadAllBtn.addEventListener('click', async function() {
        const stateCode = stateSelect.value;
        const districtCode = districtSelect.value;
        const complexCode = complexSelect.value;
        const date = dateInput.value;

        if (!stateCode || !districtCode || !complexCode) {
            showResult(result, 'Please select state, district, and court complex', 'warning');
            return;
        }

        const formattedDate = new Date(date).toLocaleDateString('en-GB').replace(/\//g, '/');

        showLoading(loading);
        result.innerHTML = '';

        try {
            const response = await fetch('/api/download-all-causelists', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    state_code: stateCode,
                    district_code: districtCode,
                    complex_code: complexCode,
                    date: formattedDate
                })
            });

            const data = await response.json();
            hideLoading(loading);

            if (data.success) {
                let filesList = data.files.map(f => `
                    <li>${f} 
                        <a href="/api/download-file/${f}" class="btn btn-sm btn-primary ms-2" download>
                            <i class="fas fa-download"></i> Download
                        </a>
                    </li>
                `).join('');
                showResult(result, `
                    <i class="fas fa-check-circle"></i> <strong>Success!</strong><br>
                    ${data.message}<br>
                    <strong>Total Cases:</strong> ${data.total_cases}<br>
                    <strong>PDF Files:</strong>
                    <ul>${filesList}</ul>
                `, 'success');
            } else {
                showResult(result, `<i class="fas fa-exclamation-triangle"></i> Error: ${data.error}`, 'danger');
            }
        } catch (error) {
            hideLoading(loading);
            showResult(result, `<i class="fas fa-exclamation-triangle"></i> Error: ${error.message}`, 'danger');
        }
    });

    document.getElementById('lookupForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const stateCode = lookupStateSelect.value;
        const districtCode = lookupDistrictSelect.value;
        const cnr = document.getElementById('cnr').value.trim();
        const caseType = document.getElementById('caseType').value.trim();
        const caseNumber = document.getElementById('caseNumber').value.trim();
        const caseYear = document.getElementById('caseYear').value.trim();

        if (!stateCode || !districtCode) {
            showResult(lookupResult, 'Please select state and district', 'warning');
            return;
        }

        if (!cnr && (!caseType || !caseNumber || !caseYear)) {
            showResult(lookupResult, 'Please enter either CNR or Case Type/Number/Year', 'warning');
            return;
        }

        showLoading(lookupLoading);
        lookupResult.innerHTML = '';

        try {
            const response = await fetch('/api/lookup-case', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    state_code: stateCode,
                    district_code: districtCode,
                    cnr: cnr,
                    case_type: caseType,
                    case_number: caseNumber,
                    case_year: caseYear
                })
            });

            const data = await response.json();
            hideLoading(lookupLoading);

            if (data.success) {
                const results = data.results;
                let resultHTML = '<div class="mt-4">';

                if (results.today && results.today.found) {
                    resultHTML += `
                        <div class="result-item">
                            <h5><i class="fas fa-check-circle text-success"></i> Listed Today</h5>
                            <p><strong>Date:</strong> ${results.today.date}</p>
                            <p><strong>Serial Number:</strong> ${results.today.serial_number}</p>
                            <p><strong>Case Number:</strong> ${results.today.case_number}</p>
                        </div>
                    `;
                } else {
                    resultHTML += `
                        <div class="result-item">
                            <h5><i class="fas fa-times-circle text-danger"></i> Not Listed Today</h5>
                        </div>
                    `;
                }

                if (results.tomorrow && results.tomorrow.found) {
                    resultHTML += `
                        <div class="result-item">
                            <h5><i class="fas fa-check-circle text-success"></i> Listed Tomorrow</h5>
                            <p><strong>Date:</strong> ${results.tomorrow.date}</p>
                            <p><strong>Serial Number:</strong> ${results.tomorrow.serial_number}</p>
                            <p><strong>Case Number:</strong> ${results.tomorrow.case_number}</p>
                        </div>
                    `;
                } else {
                    resultHTML += `
                        <div class="result-item">
                            <h5><i class="fas fa-times-circle text-danger"></i> Not Listed Tomorrow</h5>
                        </div>
                    `;
                }

                resultHTML += '</div>';
                lookupResult.innerHTML = resultHTML;
            } else {
                showResult(lookupResult, `<i class="fas fa-exclamation-triangle"></i> Error: ${data.error}`, 'danger');
            }
        } catch (error) {
            hideLoading(lookupLoading);
            showResult(lookupResult, `<i class="fas fa-exclamation-triangle"></i> Error: ${error.message}`, 'danger');
        }
    });
});

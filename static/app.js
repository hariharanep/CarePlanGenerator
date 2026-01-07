// App State variables
const AppState = {
    currentCarePlan: '',
    statsRefreshInterval: null
};

// DOM elements
const DOM = {
    // Stats
    totalOrders: () => document.getElementById('totalOrders'),
    totalPatients: () => document.getElementById('totalPatients'),
    totalProviders: () => document.getElementById('totalProviders'),
    
    // Alerts
    errorAlert: () => document.getElementById('errorAlert'),
    errorList: () => document.getElementById('errorList'),
    successAlert: () => document.getElementById('successAlert'),
    successMessage: () => document.getElementById('successMessage'),
    warningAlert: () => document.getElementById('warningAlert'),
    warningList: () => document.getElementById('warningList'),
    
    // Form fields
    patientFirstName: () => document.getElementById('patientFirstName'),
    patientLastName: () => document.getElementById('patientLastName'),
    patientMRN: () => document.getElementById('patientMRN'),
    providerName: () => document.getElementById('providerName'),
    providerNPI: () => document.getElementById('providerNPI'),
    primaryDiagnosis: () => document.getElementById('primaryDiagnosis'),
    medication: () => document.getElementById('medication'),
    additionalDiagnoses: () => document.getElementById('additionalDiagnoses'),
    medicationHistory: () => document.getElementById('medicationHistory'),
    patientRecords: () => document.getElementById('patientRecords'),
    
    // Buttons
    validateBtn: () => document.getElementById('validateBtn'),
    generateBtn: () => document.getElementById('generateBtn'),
    exportBtn: () => document.getElementById('exportBtn'),
    resetBtn: () => document.getElementById('resetBtn'),
    downloadBtn: () => document.getElementById('downloadButton'),
    
    // Output areas
    loading: () => document.getElementById('loading'),
    loadingMessage: () => document.getElementById('loadingMessage'),
    carePlanOutput: () => document.getElementById('carePlanOutput'),
    carePlanContent: () => document.getElementById('carePlanContent'),
    
    // Form
    form: () => document.getElementById('carePlanForm')
};

// API Call Functions
const APIClient = {

    // fetch stats API call
    async fetchStats() {
        const response = await fetch('/care-plan/stats', {
            cache: 'no-cache',
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Unexpected Error`);
        }

        const payload = await response.json();
        return payload;
    },

    // validate order API call
    async validateOrder(formData) {
        const response = await fetch('/care-plan/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const payload = await response.json();
        if (response.ok) {
            return {
                success: true,
                warnings: payload.warnings,
                sanitized_data: payload.sanitized_data
            };
        }
        else {
            return {
                success: false,
                errors: payload.errors
            };
        }
    },

    // submit order API call
    async submitOrder(order) {
        const response = await fetch('/care-plan/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(order)
        });

        if (response.ok) {
            return {
                success: true,
            };
        }
        else {
            const payload = await response.json();
            return {
                success: false,
                errors: payload.errors
            };
        }
    },

    // generate care plan API call
    async generateCarePlan(formData) {
        const response = await fetch('/care-plan/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const payload = await response.json();

        if (response.ok) {
            return {
                success: true,
                full_order: payload.full_order,
                warnings: payload.warnings
            }
        }
        else {
            return {
                success: false,
                errors: payload.errors
            }

        }
    },

    // export orders API call
    async exportOrders() {
        const response = await fetch('/care-plan/orders');
        
        if (!response.ok) {
            payload = await response.json();
            throw new Error(payload.error);
        }
        const blob = await response.blob();
        return blob;
    }
};

// Form helper methods
const FormFields = {

    // collect all form fields
    collect() {
        return {
            patient_first_name: DOM.patientFirstName().value,
            patient_last_name: DOM.patientLastName().value,
            patient_mrn: DOM.patientMRN().value,
            provider_name: DOM.providerName().value,
            provider_npi: DOM.providerNPI().value,
            primary_diagnosis: DOM.primaryDiagnosis().value,
            medication: DOM.medication().value,
            additional_diagnoses: DOM.additionalDiagnoses().value,
            medication_history: DOM.medicationHistory().value,
            patient_records: DOM.patientRecords().value
        };
    },

    // clear form
    clear() {
        DOM.form().reset();
    }
};

// UI helper methods
const UI = {

    
    hideAllAlerts() {
        DOM.errorAlert().style.display = 'none';
        DOM.successAlert().style.display = 'none';
        DOM.warningAlert().style.display = 'none';
    },

    // show errors produced
    showErrors(errors) {
        this.hideAllAlerts();
        const errorList = DOM.errorList();
        errorList.innerHTML = errors.map(e => `<li>${e}</li>`).join('');
        DOM.errorAlert().style.display = 'block';
    },

    // show warnings produced
    showWarnings(warnings) {
        const warningList = DOM.warningList();
        warningList.innerHTML = warnings.map(e => `<li>${e}</li>`).join('');
        DOM.warningAlert().style.display = 'block';
    },

    // show success message
    showSuccess(message) {
        DOM.successMessage().textContent = message;
        DOM.successAlert().style.display = 'block';
    },

    // set loading state appropriately when waiting for any server/API calls
    setLoadingState(isLoading, message = 'Processing...') {
        DOM.generateBtn().disabled = isLoading;
        DOM.loading().style.display = isLoading ? 'block' : 'none';
        DOM.loadingMessage().textContent = message;
    },

    // render generated care plan to DOM
    showCarePlan(carePlanText) {
        AppState.currentCarePlan = carePlanText;
        DOM.carePlanContent().textContent = carePlanText;
        DOM.carePlanOutput().style.display = 'block';
    },

    // hide care plan output
    hideCarePlan() {
        DOM.carePlanOutput().style.display = 'none';
        AppState.currentCarePlan = '';
    },

    // update the stats
    updateStats(stats) {
        DOM.totalOrders().textContent = stats.total_orders;
        DOM.totalPatients().textContent = stats.total_patients;
        DOM.totalProviders().textContent = stats.total_providers;
    },

    // render stats as loading in DOM
    setStatsLoading() {
        DOM.totalOrders().textContent = '...';
        DOM.totalPatients().textContent = '...';
        DOM.totalProviders().textContent = '...';
    },

    // render stats as '-' in DOM to represent that an error occurred
    setStatsError() {
        DOM.totalOrders().textContent = '—';
        DOM.totalPatients().textContent = '—';
        DOM.totalProviders().textContent = '—';
    }
};

// Stats Management
const StatsManager = {

    // load and update stats functionality
    async load() {
        try {
            const stats = await APIClient.fetchStats();
            UI.updateStats(stats);
        } catch (error) {
            UI.showErrors(['Failed to load stats due to an internal error']);
            UI.setStatsError();
        }
    },

    // creates interval that calls load function every intervalMs milliseconds
    startAutoRefresh(intervalMs = 2000) {
        this.stopAutoRefresh();
        AppState.statsRefreshInterval = setInterval(() => this.load(), intervalMs);
    },

    // clears and resets statsRefreshInterval to null
    stopAutoRefresh() {
        if (AppState.statsRefreshInterval) {
            clearInterval(AppState.statsRefreshInterval);
            AppState.statsRefreshInterval = null;
        }
    }
};

const ValidationService = {

    // form validation functionality
    async validate(formData) {
        UI.hideAllAlerts();
        try {
            const result = await APIClient.validateOrder(formData);
            
            if (result.success) {
                if (result.warnings) {
                    UI.showWarnings(result.warnings);
                }
                UI.showSuccess('Validation passed! You can now generate the care plan');
                return result.sanitized_data;
            } else {
                UI.showErrors(result.errors || ['Unknown validation error']);
            }
        } catch (error) {
            UI.showErrors(['Validation request failed due to an internal error']);
        }
    }
};

const CarePlanService = {

    // generate care plan
    async generateCarePlan(formData) {
        UI.setLoadingState(true, 'Generating care plan...');
        UI.hideCarePlan();
        try {    
            const result = await APIClient.generateCarePlan(formData);

            if (result.success) {
                if (result.warnings) {
                    UI.showWarnings(result.warnings);
                }
                const full_order = result.full_order
                UI.showCarePlan(full_order.care_plan);
                UI.showSuccess('Care plan generated successfully!');
                return full_order;
            } else {
                UI.showErrors(result.errors || ['Failed to generate care plan due to an internal error']);
            }
        } catch (error) {
            UI.showErrors(['Failed to generate care plan due to an internal error']);
        } finally {
            UI.setLoadingState(false);
        }
    },

    // submit full order
    async submitOrder(order) {
        UI.setLoadingState(true, 'Submitting order...');
        try {    
            const result = await APIClient.submitOrder(order);

            if (result.success) {
                UI.showSuccess('Order and Care Plan persisted successfully!');
            } else {
                UI.showErrors(result.errors || ['Failed to generate care plan due to an internal error']);
            }
        } catch (error) {
            UI.showErrors(['Failed to generate care plan due to an internal error']);
        } finally {
            UI.setLoadingState(false);
        }
    }

};

const FileOperations = {

    // export orders functionality
    async exportOrders() {
        try {
            const blob = await APIClient.exportOrders();            
            const url = window.URL.createObjectURL(blob);
            const anchor = document.createElement('a');
            anchor.href = url;
            anchor.download = `care_plans_export_${Date.now()}.csv`;
            
            document.body.appendChild(anchor);
            anchor.click();
            
            window.URL.revokeObjectURL(url);
            document.body.removeChild(anchor);
            
            UI.showSuccess('Data exported successfully!');
        } catch (error) {
            UI.showErrors([error.message || 'Export failed due to an internal error']);
        }
    },

    // download care plan functionality
    downloadCarePlan() {
        if (!AppState.currentCarePlan) {
            UI.showErrors(['No care plan to download']);
            return;
        }

        try {
            const mrn = DOM.patientMRN().value || 'unknown';
            const timestamp = new Date().toISOString()
                .replace(/[:.]/g, '-')
                .slice(0, -5);
            const filename = `care_plan_${mrn}_${timestamp}.txt`;

            const dataUri = 'data:text/plain;charset=utf-8,' + 
                           encodeURIComponent(AppState.currentCarePlan);
            
            const anchor = document.createElement('a');
            anchor.setAttribute('href', dataUri);
            anchor.setAttribute('download', filename);
            anchor.style.display = 'none';
            
            document.body.appendChild(anchor);
            anchor.click();
            document.body.removeChild(anchor);
            
            UI.showSuccess('Care plan downloaded successfully!');
        } catch (error) {
            UI.showErrors(['Download failed due to an internal error']);
        }
    }
};


const EventHandlers = {

    // validation event handler
    async handleValidate() {
        const formData = FormFields.collect();
        await ValidationService.validate(formData);
    },

    // submit order and generate care plan event handler
    async handleSubmit(event) {
        event.preventDefault();
        const formData = FormFields.collect();
        const sanitizedData = await ValidationService.validate(formData);

        if (sanitizedData) {
            const fullOrder = await CarePlanService.generateCarePlan(sanitizedData);
            if (fullOrder) {
                await CarePlanService.submitOrder(fullOrder);
                await StatsManager.load();
            }
        }
        
    },

    // handle download care plan
    handleDownload() {
        FileOperations.downloadCarePlan();  
    },

    // reset form event handler
    handleReset() {
        FormFields.clear();
        UI.hideCarePlan();
        UI.hideAllAlerts();
    },

    // export orders event handler
    async handleExport() {
        await FileOperations.exportOrders();
    }
};

function initializeApp() {
    // initialize stats and setup fetch stats auto-refresh
    UI.setStatsLoading();
    StatsManager.load();
    StatsManager.startAutoRefresh(5000);

    // Register event listeners
    DOM.validateBtn().addEventListener('click', EventHandlers.handleValidate);
    DOM.form().addEventListener('submit', EventHandlers.handleSubmit);
    DOM.resetBtn().addEventListener('click', EventHandlers.handleReset);
    DOM.exportBtn().addEventListener('click', EventHandlers.handleExport);
    DOM.downloadBtn().addEventListener('click', EventHandlers.handleDownload);

    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        StatsManager.stopAutoRefresh();
    });
}

// Start the application when DOM is ready
window.addEventListener('load', initializeApp);
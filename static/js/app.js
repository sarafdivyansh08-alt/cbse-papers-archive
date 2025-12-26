// CBSE Papers Archive - Main JavaScript

// State management
const state = {
    papers: [],
    filteredPapers: [],
    subjects: [],
    years: [],
    regions: [],
    selectedPapers: new Set(),
    currentPage: 1,
    papersPerPage: 12,
    viewMode: 'grid', // 'grid' or 'list'
    filters: {
        subject_id: null,
        year_id: null,
        region_id: null,
        paper_type: null,
        search: ''
    }
};

// DOM Elements
const elements = {
    subjectFilter: document.getElementById('subjectFilter'),
    yearFilter: document.getElementById('yearFilter'),
    regionFilter: document.getElementById('regionFilter'),
    typeFilter: document.getElementById('typeFilter'),
    searchInput: document.getElementById('searchInput'),
    papersContainer: document.getElementById('papersContainer'),
    loadingSpinner: document.getElementById('loadingSpinner'),
    noResults: document.getElementById('noResults'),
    pagination: document.getElementById('pagination'),
    selectionActions: document.getElementById('selectionActions'),
    selectedCount: document.getElementById('selectedCount'),
    totalPapers: document.getElementById('totalPapers'),
    gridView: document.getElementById('gridView'),
    listView: document.getElementById('listView'),
    selectAll: document.getElementById('selectAll'),
    clearSelection: document.getElementById('clearSelection'),
    downloadSelected: document.getElementById('downloadSelected')
};

// Initialize the application
async function init() {
    try {
        // Load initial data
        await Promise.all([
            loadSubjects(),
            loadYears(),
            loadRegions(),
            loadPapers()
        ]);
        
        // Load stats
        loadStats();
        
        // Setup event listeners
        setupEventListeners();
        
        // Hide loading spinner
        elements.loadingSpinner.style.display = 'none';
        
    } catch (error) {
        console.error('Error initializing app:', error);
        showError('Failed to load data. Please refresh the page.');
    }
}

// Load subjects from API
async function loadSubjects() {
    const response = await fetch('/api/subjects');
    state.subjects = await response.json();
    
    // Populate subject filter
    state.subjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject.id;
        option.textContent = subject.display_name;
        elements.subjectFilter.appendChild(option);
    });
}

// Load years from API
async function loadYears() {
    const response = await fetch('/api/years');
    state.years = await response.json();
    
    // Populate year filter
    state.years.forEach(year => {
        const option = document.createElement('option');
        option.value = year.id;
        option.textContent = year.year;
        elements.yearFilter.appendChild(option);
    });
}

// Load regions from API
async function loadRegions() {
    const response = await fetch('/api/regions');
    state.regions = await response.json();
    
    // Populate region filter
    state.regions.forEach(region => {
        const option = document.createElement('option');
        option.value = region.id;
        option.textContent = region.display_name;
        elements.regionFilter.appendChild(option);
    });
}

// Load papers from API
async function loadPapers() {
    const params = new URLSearchParams();
    
    if (state.filters.subject_id) params.append('subject_id', state.filters.subject_id);
    if (state.filters.year_id) params.append('year_id', state.filters.year_id);
    if (state.filters.region_id) params.append('region_id', state.filters.region_id);
    if (state.filters.paper_type) params.append('paper_type', state.filters.paper_type);
    
    const response = await fetch(`/api/papers?${params.toString()}`);
    state.papers = await response.json();
    
    // Apply search filter
    applySearchFilter();
    
    // Render papers
    renderPapers();
}

// Apply search filter
function applySearchFilter() {
    const searchTerm = state.filters.search.toLowerCase();
    
    if (searchTerm) {
        state.filteredPapers = state.papers.filter(paper => 
            paper.title.toLowerCase().includes(searchTerm) ||
            paper.subject_name.toLowerCase().includes(searchTerm) ||
            paper.region_name.toLowerCase().includes(searchTerm) ||
            paper.year.toString().includes(searchTerm)
        );
    } else {
        state.filteredPapers = [...state.papers];
    }
}

// Render papers
function renderPapers() {
    const startIndex = (state.currentPage - 1) * state.papersPerPage;
    const endIndex = startIndex + state.papersPerPage;
    const papersToShow = state.filteredPapers.slice(startIndex, endIndex);
    
    if (papersToShow.length === 0) {
        elements.papersContainer.innerHTML = '';
        elements.noResults.style.display = 'block';
        elements.pagination.style.display = 'none';
        return;
    }
    
    elements.noResults.style.display = 'none';
    elements.pagination.style.display = 'block';
    
    if (state.viewMode === 'grid') {
        renderGridView(papersToShow);
    } else {
        renderListView(papersToShow);
    }
    
    renderPagination();
}

// Render grid view
function renderGridView(papers) {
    elements.papersContainer.className = 'row g-4';
    elements.papersContainer.innerHTML = papers.map(paper => `
        <div class="col-md-6 col-lg-4">
            <div class="card paper-card h-100 ${state.selectedPapers.has(paper.id) ? 'selected' : ''}" 
                 data-paper-id="${paper.id}">
                <div class="paper-checkbox">
                    <input type="checkbox" class="form-check-input" 
                           ${state.selectedPapers.has(paper.id) ? 'checked' : ''}
                           onclick="togglePaperSelection(${paper.id}, event)">
                </div>
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span class="text-truncate">${paper.subject_name}</span>
                    <span class="badge badge-year">${paper.year}</span>
                </div>
                <div class="card-body">
                    <div class="d-flex align-items-start mb-3">
                        <div class="paper-icon ${paper.paper_type === 'question_paper' ? 'bg-primary' : 'bg-success'} bg-opacity-10 rounded me-3">
                            <i class="bi ${paper.paper_type === 'question_paper' ? 'bi-file-earmark-text text-primary' : 'bi-check-circle text-success'}"></i>
                        </div>
                        <div>
                            <h6 class="card-title mb-1">${paper.paper_type === 'question_paper' ? 'Question Paper' : 'Marking Scheme'}</h6>
                            <small class="text-muted">${paper.set_code || 'Standard'}</small>
                        </div>
                    </div>
                    <div class="d-flex flex-wrap gap-2">
                        <span class="badge bg-info text-dark">${paper.region_name}</span>
                        <span class="badge ${paper.paper_type === 'question_paper' ? 'bg-primary' : 'bg-success'}">
                            ${paper.paper_type === 'question_paper' ? 'Question Paper' : 'Solution'}
                        </span>
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">${paper.title.substring(0, 30)}...</small>
                        <button class="btn btn-primary btn-sm" onclick="downloadPaper(${paper.id})">
                            <i class="bi bi-download me-1"></i>Download
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Render list view
function renderListView(papers) {
    elements.papersContainer.className = 'list-view';
    elements.papersContainer.innerHTML = papers.map(paper => `
        <div class="paper-item ${state.selectedPapers.has(paper.id) ? 'selected' : ''}" 
             data-paper-id="${paper.id}">
            <div class="paper-info">
                <input type="checkbox" class="form-check-input me-3" 
                       ${state.selectedPapers.has(paper.id) ? 'checked' : ''}
                       onclick="togglePaperSelection(${paper.id}, event)">
                <div class="paper-icon ${paper.paper_type === 'question_paper' ? 'bg-primary' : 'bg-success'} bg-opacity-10 rounded">
                    <i class="bi ${paper.paper_type === 'question_paper' ? 'bi-file-earmark-text text-primary' : 'bi-check-circle text-success'}"></i>
                </div>
                <div class="flex-grow-1">
                    <h6 class="mb-0">${paper.title}</h6>
                    <small class="text-muted">
                        ${paper.subject_name} | ${paper.year} | ${paper.region_name} | ${paper.set_code || 'Standard'}
                    </small>
                </div>
            </div>
            <div class="paper-actions">
                <span class="badge ${paper.paper_type === 'question_paper' ? 'bg-primary' : 'bg-success'} me-2">
                    ${paper.paper_type === 'question_paper' ? 'Question Paper' : 'Solution'}
                </span>
                <button class="btn btn-primary btn-sm" onclick="downloadPaper(${paper.id})">
                    <i class="bi bi-download"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Render pagination
function renderPagination() {
    const totalPages = Math.ceil(state.filteredPapers.length / state.papersPerPage);
    const paginationList = elements.pagination.querySelector('ul');
    
    if (totalPages <= 1) {
        paginationList.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `
        <li class="page-item ${state.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${state.currentPage - 1}); return false;">
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
    `;
    
    // Page numbers
    const startPage = Math.max(1, state.currentPage - 2);
    const endPage = Math.min(totalPages, state.currentPage + 2);
    
    if (startPage > 1) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(1); return false;">1</a></li>`;
        if (startPage > 2) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === state.currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i}); return false;">${i}</a>
            </li>
        `;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${totalPages}); return false;">${totalPages}</a></li>`;
    }
    
    // Next button
    html += `
        <li class="page-item ${state.currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${state.currentPage + 1}); return false;">
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
    `;
    
    paginationList.innerHTML = html;
}

// Change page
function changePage(page) {
    const totalPages = Math.ceil(state.filteredPapers.length / state.papersPerPage);
    if (page < 1 || page > totalPages) return;
    
    state.currentPage = page;
    renderPapers();
    
    // Scroll to papers section
    document.getElementById('papers').scrollIntoView({ behavior: 'smooth' });
}

// Toggle paper selection
function togglePaperSelection(paperId, event) {
    if (event) event.stopPropagation();
    
    if (state.selectedPapers.has(paperId)) {
        state.selectedPapers.delete(paperId);
    } else {
        state.selectedPapers.add(paperId);
    }
    
    updateSelectionUI();
    renderPapers();
}

// Update selection UI
function updateSelectionUI() {
    const count = state.selectedPapers.size;
    elements.selectedCount.textContent = count;
    elements.selectionActions.style.display = count > 0 ? 'block' : 'none';
}

// Select all visible papers
function selectAllVisible() {
    const startIndex = (state.currentPage - 1) * state.papersPerPage;
    const endIndex = startIndex + state.papersPerPage;
    const visiblePapers = state.filteredPapers.slice(startIndex, endIndex);
    
    visiblePapers.forEach(paper => {
        state.selectedPapers.add(paper.id);
    });
    
    updateSelectionUI();
    renderPapers();
}

// Clear selection
function clearSelection() {
    state.selectedPapers.clear();
    updateSelectionUI();
    renderPapers();
}

// Select all filtered papers (across all pages)
function selectAllFiltered() {
  state.filteredPapers.forEach(paper => {
    state.selectedPapers.add(paper.id);
  });
  
  updateSelectionUI();
  renderPapers();
}


// Download single paper - direct PDF download
async function downloadPaper(paperId) {
    try {
        // Show loading indicator
        showLoading('Downloading PDF...');
        
        const response = await fetch(`/api/download/${paperId}`);
        
        if (response.ok) {
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/pdf')) {
                // Direct PDF download
                const blob = await response.blob();
                const contentDisposition = response.headers.get('content-disposition');
                let filename = 'paper.pdf';
                
                if (contentDisposition) {
                    const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                    if (match && match[1]) {
                        filename = match[1].replace(/['"]/g, '');
                    }
                }
                
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                
                hideLoading();
                showSuccess('PDF downloaded successfully!');
            } else {
                // JSON response (error or redirect)
                const data = await response.json();
                hideLoading();
                
                if (data.source_url) {
                    // Show modal with source URL as fallback
                    showDownloadModal(data);
                } else if (data.error) {
                    showError(data.error);
                }
            }
        } else {
            hideLoading();
            const data = await response.json();
            
            if (data.source_url) {
                showDownloadModal(data);
            } else {
                showError(data.error || 'Failed to download paper');
            }
        }
    } catch (error) {
        hideLoading();
        console.error('Error downloading paper:', error);
        showError('Failed to download paper. Please try again.');
    }
}

// Show download modal (fallback when direct download fails)
function showDownloadModal(data) {
    const modal = new bootstrap.Modal(document.getElementById('downloadModal'));
    const content = document.getElementById('downloadModalContent');
    
    content.innerHTML = `
        <div class="text-center mb-4">
            <i class="bi bi-exclamation-triangle display-1 text-warning"></i>
        </div>
        <h5 class="text-center mb-3">Direct Download Not Available</h5>
        <p class="text-muted text-center mb-3">
            The PDF could not be downloaded directly. Please visit the source page to download the paper.
        </p>
        <div class="d-grid gap-2">
            <a href="${data.source_url}" target="_blank" class="btn btn-primary">
                <i class="bi bi-box-arrow-up-right me-2"></i>Open Source Page
            </a>
        </div>
    `;
    
    modal.show();
}

// Show loading indicator
function showLoading(message = 'Loading...') {
    let loadingOverlay = document.getElementById('loadingOverlay');
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loadingOverlay';
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="loading-message mb-0">${message}</p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    } else {
        loadingOverlay.querySelector('.loading-message').textContent = message;
        loadingOverlay.style.display = 'flex';
    }
}

// Hide loading indicator
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// Download selected papers as ZIP
async function downloadSelectedPapers() {
    if (state.selectedPapers.size === 0) {
        showError('No papers selected');
        return;
    }
    
    try {
        // Show loading indicator
        showLoading(`Downloading ${state.selectedPapers.size} papers as ZIP... This may take a moment.`);
        
        const response = await fetch('/api/download-multiple', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                paper_ids: Array.from(state.selectedPapers)
            })
        });
        
        hideLoading();
        
        if (response.ok) {
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/zip')) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'cbse_papers.zip';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                
                showSuccess('ZIP file downloaded successfully!');
                clearSelection();
            } else {
                const data = await response.json();
                if (data.failed_papers && data.failed_papers.length > 0) {
                    showError(`Could not download some papers. Please try downloading them individually.`);
                } else {
                    showError(data.error || 'Failed to create ZIP file');
                }
            }
        } else {
            const data = await response.json();
            showError(data.error || 'Failed to download papers');
        }
    } catch (error) {
        hideLoading();
        console.error('Error downloading papers:', error);
        showError('Failed to download papers. Please try again.');
    }
}

// Load stats
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        elements.totalPapers.textContent = stats.total_papers;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Filter by subject (from subject cards)
function filterBySubject(subjectName) {
    const subject = state.subjects.find(s => s.name === subjectName);
    if (subject) {
        elements.subjectFilter.value = subject.id;
        state.filters.subject_id = subject.id;
        state.currentPage = 1;
        loadPapers();
        
        // Scroll to papers section
        document.getElementById('papers').scrollIntoView({ behavior: 'smooth' });
    }
}

// Setup event listeners
function setupEventListeners() {
    // Filter changes
    elements.subjectFilter.addEventListener('change', (e) => {
        state.filters.subject_id = e.target.value || null;
        state.currentPage = 1;
        loadPapers();
    });
    
    elements.yearFilter.addEventListener('change', (e) => {
        state.filters.year_id = e.target.value || null;
        state.currentPage = 1;
        loadPapers();
    });
    
    elements.regionFilter.addEventListener('change', (e) => {
        state.filters.region_id = e.target.value || null;
        state.currentPage = 1;
        loadPapers();
    });
    
    elements.typeFilter.addEventListener('change', (e) => {
        state.filters.paper_type = e.target.value || null;
        state.currentPage = 1;
        loadPapers();
    });
    
    // Search input with debounce
    let searchTimeout;
    elements.searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            state.filters.search = e.target.value;
            state.currentPage = 1;
            applySearchFilter();
            renderPapers();
        }, 300);
    });
    
    // View mode toggle
    elements.gridView.addEventListener('click', () => {
        state.viewMode = 'grid';
        elements.gridView.classList.add('active');
        elements.listView.classList.remove('active');
        renderPapers();
    });
    
    elements.listView.addEventListener('click', () => {
        state.viewMode = 'list';
        elements.listView.classList.add('active');
        elements.gridView.classList.remove('active');
        renderPapers();
    });
    
    // Selection actions
    elements.selectAll.addEventListener('click', selectAllVisible);
    elements.clearSelection.addEventListener('click', clearSelection);
    elements.downloadSelected.addEventListener('click', downloadSelectedPapers);
}

// Show error message
function showError(message) {
    showToast(message, 'danger');
}

// Show success message
function showSuccess(message) {
    showToast(message, 'success');
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi ${type === 'success' ? 'bi-check-circle' : 'bi-exclamation-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    container.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', init);

// Make functions available globally
window.togglePaperSelection = togglePaperSelection;
window.downloadPaper = downloadPaper;
window.changePage = changePage;
window.filterBySubject = filterBySubject;
window.selectAllVisible = selectAllVisible;
window.selectAllFiltered = selectAllFiltered;
window.clearSelection = clearSelection;
window.downloadSelectedPapers = downloadSelectedPapers;

// Global variables
let tinyMCEEditor;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for TinyMCE to load
    setTimeout(function() {
        initializeTinyMCEEditor();
    }, 100);
    setupEventListeners();
    showPage('add-vuln');
});

// Initialize TinyMCE rich text editor
function initializeTinyMCEEditor() {
    tinymce.init({
        selector: '#steps-editor',
        height: 300,
        min_height: 300,
        menubar: false,
        plugins: [
            'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
            'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
            'insertdatetime', 'media', 'table', 'help', 'wordcount', 'paste'
        ],
        toolbar: 'undo redo | blocks | ' +
            'bold italic forecolor | alignleft aligncenter ' +
            'alignright alignjustify | bullist numlist outdent indent | ' +
            'removeformat | help | image | link | code | table',
        content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, San Francisco, Segoe UI, Roboto, Helvetica Neue, sans-serif; font-size: 14px; }',
        image_advtab: true,
        image_caption: true,
        image_description: true,
        image_title: true,
        image_dimensions: true,
        image_class_list: [
            {title: 'Responsive', value: 'img-responsive'},
            {title: 'Rounded', value: 'img-rounded'},
            {title: 'Circle', value: 'img-circle'},
            {title: 'Thumbnail', value: 'img-thumbnail'}
        ],
        image_upload_handler: function (blobInfo, success, failure) {
            // Convert blob to base64 for embedding
            const reader = new FileReader();
            reader.onload = function() {
                success(reader.result);
            };
            reader.onerror = function() {
                failure('Image upload failed');
            };
            reader.readAsDataURL(blobInfo.blob());
        },
        paste_data_images: true,
        paste_enable_default_filters: false,
        paste_preprocess: function(plugin, args) {
            // Handle pasted images before processing
            const content = args.content;
            // Convert file references to base64 images
            args.content = content.replace(/file:\/\/\/[^"]+/g, function(match) {
                // This will be handled by the paste_postprocess
                return match;
            });
        },
        paste_postprocess: function(plugin, args) {
            // Handle pasted images and convert to base64
            const images = args.node.querySelectorAll('img');
            images.forEach(img => {
                // If image src is a file path, convert to base64
                if (img.src && img.src.startsWith('file://')) {
                    // Remove file:// prefix and convert to base64
                    const filePath = img.src.replace('file://', '');
                    // For now, we'll handle this in the image upload handler
                    img.style.maxWidth = '100%';
                    img.style.height = 'auto';
                    img.style.borderRadius = '6px';
                    img.style.margin = '10px 0';
                    img.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                } else {
                    img.style.maxWidth = '100%';
                    img.style.height = 'auto';
                    img.style.borderRadius = '6px';
                    img.style.margin = '10px 0';
                    img.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                }
            });
        },
        setup: function (editor) {
            tinyMCEEditor = editor;
            
            // Add custom image resize functionality
            editor.on('init', function() {
                console.log('TinyMCE initialized successfully');
                // Add custom CSS for better image handling
                const style = document.createElement('style');
                style.textContent = `
                    .tox-edit-area__iframe body img {
                        max-width: 100% !important;
                        height: auto !important;
                        border-radius: 6px !important;
                        margin: 10px 0 !important;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
                        cursor: pointer !important;
                    }
                    .tox-edit-area__iframe body img:hover {
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
                        transform: scale(1.02);
                        transition: all 0.2s ease;
                    }
                `;
                document.head.appendChild(style);
            });
            
            // Handle image click for preview
            editor.on('click', function(e) {
                if (e.target.tagName === 'IMG') {
                    showImagePreview(e.target.src);
                }
            });
            
            // Handle paste events for images
            editor.on('paste', function(e) {
                const clipboardData = e.clipboardData || window.clipboardData;
                const items = clipboardData.items;
                
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    if (item.type.indexOf('image') !== -1) {
                        const file = item.getAsFile();
                        const reader = new FileReader();
                        
                        reader.onload = function(e) {
                            // Insert the image into the editor
                            editor.insertContent('<img src="' + e.target.result + '" style="max-width: 100%; height: auto; border-radius: 6px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />');
                        };
                        
                        reader.readAsDataURL(file);
                        e.preventDefault();
                        break;
                    }
                }
            });
        },
        init_instance_callback: function (editor) {
            console.log('TinyMCE instance created');
            // Force proper height after initialization
            setTimeout(() => {
                const container = editor.getContainer();
                if (container) {
                    container.style.height = '300px';
                    container.style.minHeight = '300px';
                }
            }, 100);
        }
    }).then(function() {
        console.log('TinyMCE initialization completed');
    });
}

// Image preview modal functionality
function showImagePreview(src) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('imagePreviewModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'imagePreviewModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Image Preview</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img id="previewImage" src="" class="img-fluid" style="max-height: 70vh;">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-danger" id="removeImageBtn">Remove Image</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    // Set image source and show modal
    document.getElementById('previewImage').src = src;
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Handle remove button
    document.getElementById('removeImageBtn').onclick = function() {
        // Find and remove the image from the editor
        const editorBody = tinyMCEEditor.getBody();
        const images = editorBody.querySelectorAll('img');
        images.forEach(img => {
            if (img.src === src) {
                img.remove();
            }
        });
        bsModal.hide();
    };
}

// Setup event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('vulnerability-form').addEventListener('submit', handleFormSubmit);
    
    // Title input for AI generation
    document.getElementById('title').addEventListener('blur', function() {
        if (this.value.trim() && !document.getElementById('description').value) {
            // Auto-generate if description is empty
            generateWithAI();
        }
    });
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    // Get content from TinyMCE or fallback to textarea
    let stepsContent;
    if (tinyMCEEditor && typeof tinyMCEEditor.getContent === 'function') {
        stepsContent = tinyMCEEditor.getContent();
    } else {
        // Fallback to textarea value
        const textarea = document.getElementById('steps-editor');
        stepsContent = textarea ? textarea.value : '';
    }
    formData.set('steps_to_reproduce', stepsContent);
    
    try {
        const response = await fetch('/api/save-vulnerability', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('success', result.message);
            resetForm();
        } else {
            showAlert('danger', 'Error saving vulnerability: ' + result.message);
        }
    } catch (error) {
        showAlert('danger', 'Error saving vulnerability: ' + error.message);
    }
}

// Generate vulnerability details with AI
async function generateWithAI() {
    const title = document.getElementById('title').value.trim();
    
    if (!title) {
        showAlert('warning', 'Please enter a vulnerability title first');
        return;
    }
    
    // Show loading modal
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show();
    
    try {
        const formData = new FormData();
        formData.set('title', title);
        
        const response = await fetch('/api/generate-vulnerability-details', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            populateFormWithAI(result.data);
            showAlert('success', 'AI-generated content loaded successfully!');
        } else {
            // Show proper error message
            const errorMessage = result.message || result.detail || 'Unknown error occurred';
            showAlert('danger', `AI Error: ${errorMessage}`);
        }
    } catch (error) {
        showAlert('danger', 'Error generating content: ' + error.message);
    } finally {
        loadingModal.hide();
    }
}

// Populate form with AI-generated content
function populateFormWithAI(data) {
    document.getElementById('description').value = data.description || '';
    document.getElementById('remediation').value = data.remediation || '';
    document.getElementById('cwe_id').value = data.cwe_id || '';
    document.getElementById('owasp_category').value = data.owasp_category || '';
    document.getElementById('impact').value = data.impact_level || 'Medium';
    document.getElementById('likelihood').value = data.likelihood_level || 'Medium';
    
    // Populate references
    if (data.references && data.references.length > 0) {
        document.getElementById('references').value = data.references.join('\n');
    }
    
    // Show AI suggestions section
    const aiSection = document.getElementById('ai-suggestions');
    const aiContent = document.getElementById('ai-content');
    
    aiContent.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <strong>Description:</strong>
                <p class="small">${data.description || 'Not generated'}</p>
            </div>
            <div class="col-md-6">
                <strong>Remediation:</strong>
                <p class="small">${data.remediation || 'Not generated'}</p>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <strong>CWE ID:</strong> ${data.cwe_id || 'Not generated'}
            </div>
            <div class="col-md-6">
                <strong>OWASP Category:</strong> ${data.owasp_category || 'Not generated'}
            </div>
        </div>
    `;
    
    aiSection.style.display = 'block';
}

// Show page
function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });
    
    // Show selected page
    document.getElementById(pageName + '-page').style.display = 'block';
    
    // Load data for specific pages
    if (pageName === 'view-reports') {
        loadReports();
    } else if (pageName === 'export') {
        loadExportPage();
    }
}

// Load reports
async function loadReports() {
    try {
        const response = await fetch('/api/vulnerabilities');
        const result = await response.json();
        
        if (result.success) {
            displayReports(result.data);
        } else {
            showAlert('danger', 'Error loading reports: ' + result.message);
        }
    } catch (error) {
        showAlert('danger', 'Error loading reports: ' + error.message);
    }
}

// Display reports
function displayReports(reports) {
    const summaryDiv = document.getElementById('reports-summary');
    const listDiv = document.getElementById('reports-list');
    
    if (reports.length === 0) {
        listDiv.innerHTML = '<div class="alert alert-info">No vulnerabilities found. Add some vulnerabilities first!</div>';
        summaryDiv.innerHTML = '';
        return;
    }
    
    // Generate summary
    const total = reports.length;
    const open = reports.filter(r => r.status === 'Open').length;
    const critical = reports.filter(r => r.impact === 'Critical').length;
    const high = reports.filter(r => r.impact === 'High').length;
    
    summaryDiv.innerHTML = `
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">${total}</h5>
                    <p class="card-text">Total Vulnerabilities</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title text-warning">${open}</h5>
                    <p class="card-text">Open Issues</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title text-danger">${critical}</h5>
                    <p class="card-text">Critical</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title text-warning">${high}</h5>
                    <p class="card-text">High</p>
                </div>
            </div>
        </div>
    `;
    
    // Generate reports list
    listDiv.innerHTML = reports.map(report => `
        <div class="card vulnerability-card severity-${report.impact.toLowerCase()} mb-3">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">${report.title}</h6>
                <div>
                    <span class="badge bg-${getSeverityColor(report.impact)}">${report.impact}</span>
                    <span class="badge bg-secondary">${report.status}</span>
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="deleteReport('${report.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="card-body">
                <p class="card-text">${report.description}</p>
                <div class="row">
                    <div class="col-md-6">
                        <small class="text-muted">
                            <strong>Location:</strong> ${report.location}<br>
                            <strong>CWE:</strong> ${report.cwe_id}<br>
                            <strong>OWASP:</strong> ${report.owasp_category}
                        </small>
                    </div>
                    <div class="col-md-6">
                        <small class="text-muted">
                            <strong>Created:</strong> ${new Date(report.created_date).toLocaleDateString()}<br>
                            <strong>Instances:</strong> ${report.instances}
                        </small>
                    </div>
                </div>
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewReportDetails('${report.id}')">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Get severity color
function getSeverityColor(severity) {
    const colors = {
        'Critical': 'danger',
        'High': 'warning',
        'Medium': 'info',
        'Low': 'success'
    };
    return colors[severity] || 'secondary';
}

// Delete report
async function deleteReport(id) {
    if (confirm('Are you sure you want to delete this vulnerability?')) {
        try {
            const response = await fetch(`/api/vulnerabilities/${id}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert('success', 'Vulnerability deleted successfully');
                loadReports();
            } else {
                showAlert('danger', 'Error deleting vulnerability: ' + result.message);
            }
        } catch (error) {
            showAlert('danger', 'Error deleting vulnerability: ' + error.message);
        }
    }
}

// View report details
function viewReportDetails(id) {
    // This would open a modal or navigate to a details page
    // For now, just show an alert
    showAlert('info', 'Report details view - to be implemented');
}

// Load export page
async function loadExportPage() {
    // Export page is now handled by the buttons, no need to load content
    document.getElementById('export-content').innerHTML = '';
}

// Export report function
async function exportReport(format) {
    try {
        const response = await fetch(`/api/export-report?format=${format}`);
        
        if (format === 'pdf') {
            // Handle PDF download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `pentest_report_${new Date().toISOString().slice(0,19).replace(/:/g, '-')}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            showAlert('success', 'PDF report downloaded successfully!');
        } else {
            // Handle Markdown download
            const result = await response.json();
            if (result.success) {
                const blob = new Blob([result.report], { type: 'text/markdown' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = result.filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                showAlert('success', 'Markdown report downloaded successfully!');
            } else {
                showAlert('danger', 'Error exporting report: ' + result.message);
            }
        }
    } catch (error) {
        showAlert('danger', 'Error exporting report: ' + error.message);
    }
}

// Reset form
function resetForm() {
    document.getElementById('vulnerability-form').reset();
    if (tinyMCEEditor && typeof tinyMCEEditor.setContent === 'function') {
        tinyMCEEditor.setContent('');
    } else {
        const textarea = document.getElementById('steps-editor');
        if (textarea) {
            textarea.value = '';
        }
    }
    document.getElementById('ai-suggestions').style.display = 'none';
}

// Show alert
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// CareerGraph - Frontend JavaScript

let currentRoadmap = null;
let cy = null;

// Color scheme by level
const levelColors = {
    0: '#ec4899',  // Root - Pink
    1: '#8b5cf6',  // Main topics - Purple
    2: '#3b82f6',  // Subtopics - Blue
    3: '#10b981'   // Units - Green
};

// ===== API Key Management =====

// Check if API keys are set on page load
document.addEventListener('DOMContentLoaded', () => {
    updateKeyStatus();
});

// Save API keys to sessionStorage
function saveApiKeys() {
    const openaiKey = document.getElementById('openaiKey').value.trim();
    const serperKey = document.getElementById('serperKey').value.trim();
    
    if (!openaiKey) {
        alert('OpenAI API Key is required');
        return;
    }
    
    // Save to sessionStorage (more secure than localStorage)
    sessionStorage.setItem('openai_api_key', openaiKey);
    if (serperKey) {
        sessionStorage.setItem('serper_api_key', serperKey);
    }
    
    // Update status indicators
    updateKeyStatus();
    
    // Show success message
    alert('✅ API Keys saved successfully! You can now generate roadmaps.');
    
    // Show the query input section
    document.getElementById('apiConfigSection').style.display = 'none';
    document.getElementById('inputSection').style.display = 'block';
    document.getElementById('queryInput').focus();
}

// Toggle password visibility
function toggleKeyVisibility(inputId) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
}

// Update key status indicators
function updateKeyStatus() {
    const openaiKey = sessionStorage.getItem('openai_api_key');
    const serperKey = sessionStorage.getItem('serper_api_key');
    
    const openaiStatus = document.getElementById('openaiStatus');
    const serperStatus = document.getElementById('serperStatus');
    
    if (openaiKey) {
        openaiStatus.textContent = '✓ Set';
        openaiStatus.className = 'key-status set';
    } else {
        openaiStatus.textContent = 'Not set';
        openaiStatus.className = 'key-status not-set';
    }
    
    if (serperKey) {
        serperStatus.textContent = '✓ Set';
        serperStatus.className = 'key-status set';
    } else {
        serperStatus.textContent = 'Not set';
        serperStatus.className = 'key-status not-set';
    }
    
    // If keys are already set, skip to query input
    if (openaiKey) {
        document.getElementById('apiConfigSection').style.display = 'none';
        document.getElementById('inputSection').style.display = 'block';
    }
}

// Get API keys from sessionStorage
function getApiKeys() {
    return {
        openai_api_key: sessionStorage.getItem('openai_api_key'),
        serper_api_key: sessionStorage.getItem('serper_api_key')
    };
}

// ===== Roadmap Generation =====

// Fill example query
function fillExample(text) {
    document.getElementById('queryInput').value = text;
}

// Form submission handler
document.getElementById('queryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('queryInput').value.trim();
    
    if (query.length < 5) {
        showError('Please enter a more detailed query (at least 5 characters)');
        return;
    }
    
    await generateRoadmap(query);
});

// Generate roadmap
async function generateRoadmap(query) {
    // Show loading, hide others
    document.getElementById('inputSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'block';
    document.getElementById('roadmapSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    
    // Animate agent steps
    simulateAgentProgress();
    
    try {
        // Get API keys from sessionStorage
        const apiKeys = getApiKeys();
        
        if (!apiKeys.openai_api_key) {
            throw new Error('OpenAI API Key is required. Please configure your API keys.');
        }
        
        const response = await fetch('/api/generate-roadmap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                query,
                openai_api_key: apiKeys.openai_api_key,
                serper_api_key: apiKeys.serper_api_key
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate roadmap');
        }
        
        const roadmap = await response.json();
        currentRoadmap = roadmap;
        
        // Display roadmap
        displayRoadmap(roadmap);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}

// Simulate agent progress animation
function simulateAgentProgress() {
    const steps = ['step1', 'step2', 'step3'];
    
    steps.forEach((stepId, index) => {
        setTimeout(() => {
            const step = document.getElementById(stepId);
            step.classList.add('active');
            const status = step.querySelector('.step-status');
            status.textContent = '⏳';
            
            setTimeout(() => {
                step.classList.remove('active');
                step.classList.add('completed');
                status.textContent = '✅';
            }, 8000 + (index * 2000));
        }, index * 10000);
    });
}

// Display roadmap
function displayRoadmap(roadmap) {
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('roadmapSection').style.display = 'block';
    
    // Set header info
    document.getElementById('roadmapTitle').textContent = roadmap.title;
    document.getElementById('roadmapDescription').textContent = roadmap.description;
    
    // Set stats
    const statsHtml = `
        <div class="stat-card">
            <div class="stat-label">Total Nodes</div>
            <div class="stat-value">${roadmap.nodes.length}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Estimated Time</div>
            <div class="stat-value">${roadmap.total_time || 'Varies'}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Main Topics</div>
            <div class="stat-value">${roadmap.nodes.filter(n => n.level === 1).length}</div>
        </div>
    `;
    document.getElementById('roadmapStats').innerHTML = statsHtml;
    
    // Initialize graph
    initializeGraph(roadmap);
}

// Initialize Cytoscape graph
function initializeGraph(roadmap) {
    const elements = [];
    
    // Add nodes
    roadmap.nodes.forEach(node => {
        elements.push({
            data: {
                id: node.id,
                label: node.title,
                description: node.description,
                level: node.level,
                parent: node.parent_id,
                resources: node.resources,
                prerequisites: node.prerequisites,
                estimated_time: node.estimated_time,
                color: levelColors[node.level] || '#6b7280'
            }
        });
    });
    
    // Add edges based on parent-child relationships
    roadmap.nodes.forEach(node => {
        if (node.parent_id) {
            elements.push({
                data: {
                    id: `edge-${node.parent_id}-${node.id}`,
                    source: node.parent_id,
                    target: node.id
                }
            });
        }
    });
    
    // Initialize Cytoscape
    cy = cytoscape({
        container: document.getElementById('cy'),
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'background-color': 'data(color)',
                    'color': '#ffffff',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-size': '14px',
                    'font-weight': '600',
                    'width': 'label',
                    'height': 'label',
                    'padding': '12px',
                    'text-wrap': 'wrap',
                    'text-max-width': '180px',
                    'border-width': 3,
                    'border-color': '#ffffff',
                    'border-opacity': 0.3,
                    'transition-property': 'background-color, border-color, border-width',
                    'transition-duration': '0.3s',
                    'shadow-blur': 10,
                    'shadow-color': 'data(color)',
                    'shadow-opacity': 0.3,
                    'shadow-offset-x': 0,
                    'shadow-offset-y': 4
                }
            },
            {
                selector: 'node:hover',
                style: {
                    'border-width': 4,
                    'border-opacity': 0.8,
                    'shadow-blur': 20,
                    'shadow-opacity': 0.6
                }
            },
            {
                selector: 'node:active',
                style: {
                    'overlay-opacity': 0,
                    'border-width': 5,
                    'border-color': '#ffffff'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#4a5568',
                    'target-arrow-color': '#4a5568',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'arrow-scale': 1.5,
                    'opacity': 0.6
                }
            },
            {
                selector: 'edge:hover',
                style: {
                    'line-color': '#8b5cf6',
                    'target-arrow-color': '#8b5cf6',
                    'opacity': 1,
                    'width': 4
                }
            }
        ],
        layout: {
            name: 'breadthfirst',
            directed: true,
            spacingFactor: 1.8,
            padding: 40,
            animate: true,
            animationDuration: 1000,
            avoidOverlap: true,
            nodeDimensionsIncludeLabels: true
        },
        minZoom: 0.3,
        maxZoom: 3,
        wheelSensitivity: 0.2
    });
    
    // Node click handler
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        const data = node.data();
        
        displayNodeDetails(data);
        
        // Highlight connected nodes
        cy.elements().removeClass('highlighted');
        node.addClass('highlighted');
        node.connectedEdges().addClass('highlighted');
    });
    
    // Double-click to focus
    cy.on('dbltap', 'node', function(evt) {
        const node = evt.target;
        cy.animate({
            fit: {
                eles: node.neighborhood().add(node),
                padding: 50
            },
            duration: 500
        });
    });
}

// Display node details
function displayNodeDetails(data) {
    let resourcesHtml = '';
    
    if (data.resources && data.resources.length > 0) {
        resourcesHtml = '<h3>📚 Learning Resources</h3><div class="resource-list">';
        data.resources.forEach(resource => {
            const typeEmoji = {
                'video': '🎥',
                'documentation': '📖',
                'course': '🎓',
                'book': '📚',
                'paper': '📄'
            }[resource.type] || '📎';
            
            resourcesHtml += `
                <div class="resource-item">
                    <div class="resource-title">${typeEmoji} ${resource.title}</div>
                    <div class="resource-meta">
                        <span>Type: ${resource.type}</span>
                        ${resource.duration ? `<span>⏱️ ${resource.duration}</span>` : ''}
                    </div>
                    <div class="resource-desc">${resource.description}</div>
                    <a href="${resource.url}" target="_blank" class="resource-link">
                        Open Resource →
                    </a>
                </div>
            `;
        });
        resourcesHtml += '</div>';
    } else {
        resourcesHtml = '<p style="color: #a0a0a0; margin-top: 1rem;">No specific resources for this node. Check child nodes for detailed resources.</p>';
    }
    
    const prerequisitesHtml = data.prerequisites && data.prerequisites.length > 0
        ? `<p style="color: #b0b0b0; margin-top: 0.5rem;"><strong>Prerequisites:</strong> ${data.prerequisites.join(', ')}</p>`
        : '';
    
    const detailsHtml = `
        <h2>${data.label}</h2>
        <p style="color: #b0b0b0; margin-bottom: 1rem; line-height: 1.6;">${data.description}</p>
        ${data.estimated_time ? `<p style="color: #a0a0a0;"><strong>⏱️ Estimated Time:</strong> ${data.estimated_time}</p>` : ''}
        ${prerequisitesHtml}
        ${resourcesHtml}
    `;
    
    const detailsDiv = document.getElementById('nodeDetails');
    detailsDiv.innerHTML = detailsHtml;
    detailsDiv.style.display = 'block';
    
    // Smooth scroll to details
    setTimeout(() => {
        detailsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// Graph controls
function resetZoom() {
    if (cy) {
        cy.fit();
        cy.center();
    }
}

function fitGraph() {
    if (cy) {
        cy.fit(null, 50);
    }
}

function centerGraph() {
    if (cy) {
        cy.center();
    }
}

// Export roadmap
async function exportRoadmap() {
    if (!currentRoadmap) {
        alert('No roadmap to export');
        return;
    }
    
    try {
        const response = await fetch('/api/export-roadmap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                roadmap: currentRoadmap,
                include_styles: true
            })
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `roadmap_${currentRoadmap.title.replace(/[^a-z0-9]/gi, '_')}.html`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Export error:', error);
        alert('Failed to export roadmap. Please try again.');
    }
}

// Reset app
function resetApp() {
    document.getElementById('inputSection').style.display = 'block';
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('roadmapSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    
    document.getElementById('queryInput').value = '';
    document.getElementById('queryInput').focus();
    
    currentRoadmap = null;
    if (cy) {
        cy.destroy();
        cy = null;
    }
    
    // Reset agent steps
    ['step1', 'step2', 'step3'].forEach(stepId => {
        const step = document.getElementById(stepId);
        step.classList.remove('active', 'completed');
        const status = step.querySelector('.step-status');
        status.textContent = '⏳';
    });
}

// Show error
function showError(message) {
    document.getElementById('inputSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('roadmapSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'block';
    
    document.getElementById('errorMessage').textContent = message;
}

// Auto-focus input on load
window.addEventListener('load', () => {
    document.getElementById('queryInput').focus();
});

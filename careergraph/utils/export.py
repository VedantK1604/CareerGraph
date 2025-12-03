"""HTML export functionality for roadmaps."""
from careergraph.models.schemas import RoadmapResponse
import json


def generate_html_export(roadmap: RoadmapResponse) -> str:
    """Generate a standalone HTML file with the interactive roadmap."""
    
    # Convert roadmap to JSON for embedding
    roadmap_json = json.dumps(roadmap.model_dump(), indent=2)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{roadmap.title} - CareerGraph</title>
    <script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        .header {{
            background: rgba(26, 26, 46, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(147, 51, 234, 0.3);
            padding: 2rem;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            color: #a0a0a0;
            font-size: 1.1rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .info-card {{
            background: rgba(26, 26, 46, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .info-card h2 {{
            color: #8b5cf6;
            margin-bottom: 0.5rem;
            font-size: 1.3rem;
        }}
        
        .info-card p {{
            color: #b0b0b0;
            line-height: 1.6;
        }}
        
        .stats {{
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}
        
        .stat {{
            flex: 1;
            min-width: 200px;
            background: rgba(139, 92, 246, 0.1);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid rgba(139, 92, 246, 0.2);
        }}
        
        .stat-label {{
            color: #8b5cf6;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.3rem;
        }}
        
        .stat-value {{
            color: #e0e0e0;
            font-size: 1.5rem;
            font-weight: 600;
        }}
        
        #cy {{
            width: 100%;
            height: 600px;
            background: rgba(26, 26, 46, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            margin-bottom: 2rem;
        }}
        
        .controls {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}
        
        .btn {{
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);
        }}
        
        .legend {{
            background: rgba(26, 26, 46, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .legend h3 {{
            color: #8b5cf6;
            margin-bottom: 1rem;
        }}
        
        .legend-items {{
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        
        .node-details {{
            background: rgba(26, 26, 46, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
            display: none;
        }}
        
        .node-details.active {{
            display: block;
        }}
        
        .resource-list {{
            margin-top: 1rem;
        }}
        
        .resource-item {{
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            transition: all 0.3s ease;
        }}
        
        .resource-item:hover {{
            border-color: rgba(139, 92, 246, 0.5);
            transform: translateX(5px);
        }}
        
        .resource-title {{
            color: #8b5cf6;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }}
        
        .resource-meta {{
            color: #a0a0a0;
            font-size: 0.9rem;
            display: flex;
            gap: 1rem;
            margin-bottom: 0.5rem;
        }}
        
        .resource-desc {{
            color: #b0b0b0;
            font-size: 0.95rem;
            line-height: 1.5;
        }}
        
        .resource-link {{
            color: #ec4899;
            text-decoration: none;
            font-size: 0.9rem;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            margin-top: 0.5rem;
        }}
        
        .resource-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{roadmap.title}</h1>
        <p>{roadmap.description}</p>
    </div>
    
    <div class="container">
        <div class="info-card">
            <h2>Roadmap Overview</h2>
            <p><strong>Generated:</strong> {roadmap.generated_at}</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-label">Total Nodes</div>
                    <div class="stat-value">{len(roadmap.nodes)}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Estimated Time</div>
                    <div class="stat-value">{roadmap.total_time or 'Varies'}</div>
                </div>
            </div>
        </div>
        
        <div class="legend">
            <h3>Node Levels</h3>
            <div class="legend-items">
                <div class="legend-item">
                    <div class="legend-color" style="background: #ec4899;"></div>
                    <span>Root Goal</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #8b5cf6;"></div>
                    <span>Main Topics</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #3b82f6;"></div>
                    <span>Subtopics</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #10b981;"></div>
                    <span>Learning Units</span>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="resetZoom()">Reset View</button>
            <button class="btn" onclick="expandAll()">Expand All</button>
            <button class="btn" onclick="collapseAll()">Collapse All</button>
        </div>
        
        <div id="cy"></div>
        
        <div id="nodeDetails" class="node-details"></div>
    </div>
    
    <script>
        // Embedded roadmap data
        const roadmapData = {roadmap_json};
        
        // Color scheme by level
        const levelColors = {{
            0: '#ec4899',  // Root - Pink
            1: '#8b5cf6',  // Main topics - Purple
            2: '#3b82f6',  // Subtopics - Blue
            3: '#10b981'   // Units - Green
        }};
        
        // Prepare Cytoscape elements
        const elements = [];
        
        // Add nodes
        roadmapData.nodes.forEach(node => {{
            elements.push({{
                data: {{
                    id: node.id,
                    label: node.title,
                    description: node.description,
                    level: node.level,
                    parent: node.parent_id,
                    resources: node.resources,
                    prerequisites: node.prerequisites,
                    estimated_time: node.estimated_time,
                    color: levelColors[node.level] || '#6b7280'
                }}
            }});
        }});
        
        // Add edges based on parent-child relationships
        roadmapData.nodes.forEach(node => {{
            if (node.parent_id) {{
                elements.push({{
                    data: {{
                        id: `edge-${{node.parent_id}}-${{node.id}}`,
                        source: node.parent_id,
                        target: node.id
                    }}
                }});
            }}
        }});
        
        // Initialize Cytoscape
        const cy = cytoscape({{
            container: document.getElementById('cy'),
            elements: elements,
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'label': 'data(label)',
                        'background-color': 'data(color)',
                        'color': '#ffffff',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '12px',
                        'width': 'label',
                        'height': 'label',
                        'padding': '10px',
                        'text-wrap': 'wrap',
                        'text-max-width': '150px',
                        'border-width': 2,
                        'border-color': '#ffffff',
                        'border-opacity': 0.3,
                        'transition-property': 'background-color, border-color',
                        'transition-duration': '0.3s'
                    }}
                }},
                {{
                    selector: 'node:active',
                    style: {{
                        'overlay-opacity': 0,
                        'border-width': 3,
                        'border-color': '#ffffff'
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'width': 2,
                        'line-color': '#4a5568',
                        'target-arrow-color': '#4a5568',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'arrow-scale': 1.5
                    }}
                }},
                {{
                    selector: 'edge:active',
                    style: {{
                        'overlay-opacity': 0
                    }}
                }}
            ],
            layout: {{
                name: 'breadthfirst',
                directed: true,
                spacingFactor: 1.5,
                padding: 30,
                animate: true,
                animationDuration: 500
            }}
        }});
        
        // Node click handler
        cy.on('tap', 'node', function(evt) {{
            const node = evt.target;
            const data = node.data();
            
            let resourcesHtml = '';
            if (data.resources && data.resources.length > 0) {{
                resourcesHtml = '<h3 style="color: #8b5cf6; margin-bottom: 1rem;">Learning Resources</h3><div class="resource-list">';
                data.resources.forEach(resource => {{
                    resourcesHtml += `
                        <div class="resource-item">
                            <div class="resource-title">${{resource.title}}</div>
                            <div class="resource-meta">
                                <span>📚 ${{resource.type}}</span>
                                ${{resource.duration ? `<span>⏱️ ${{resource.duration}}</span>` : ''}}
                            </div>
                            <div class="resource-desc">${{resource.description}}</div>
                            <a href="${{resource.url}}" target="_blank" class="resource-link">
                                Open Resource →
                            </a>
                        </div>
                    `;
                }});
                resourcesHtml += '</div>';
            }} else {{
                resourcesHtml = '<p style="color: #a0a0a0;">No resources available for this node.</p>';
            }}
            
            const detailsHtml = `
                <h2 style="color: #8b5cf6; margin-bottom: 0.5rem;">${{data.label}}</h2>
                <p style="color: #b0b0b0; margin-bottom: 1rem;">${{data.description}}</p>
                ${{data.estimated_time ? `<p style="color: #a0a0a0;"><strong>Estimated Time:</strong> ${{data.estimated_time}}</p>` : ''}}
                ${{resourcesHtml}}
            `;
            
            const detailsDiv = document.getElementById('nodeDetails');
            detailsDiv.innerHTML = detailsHtml;
            detailsDiv.classList.add('active');
            detailsDiv.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
        }});
        
        // Control functions
        function resetZoom() {{
            cy.fit();
            cy.center();
        }}
        
        function expandAll() {{
            cy.expandCollapse('get').expandRecursively(cy.nodes());
        }}
        
        function collapseAll() {{
            cy.nodes().forEach(node => {{
                if (node.data('level') > 1) {{
                    node.hide();
                }}
            }});
        }}
    </script>
</body>
</html>"""
    
    return html_content

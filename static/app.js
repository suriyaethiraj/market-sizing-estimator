document.addEventListener('DOMContentLoaded', () => {
    
    // --- Elements ---
    const form = document.getElementById('sizing-form');
    const providerSelect = document.getElementById('provider');
    const apiKeyInput = document.getElementById('api-key');
    const apiKeyLabel = document.getElementById('api-key-label');
    const submitBtn = document.getElementById('submit-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    const errorMsg = document.getElementById('error-msg');
    
    const formSection = document.getElementById('form-section');
    const reportSection = document.getElementById('report-section');
    const btnBack = document.getElementById('btn-back');

    let currentReport = null; // Store the report object for exports

    // --- Custom Geographies Multi-Select Logic ---
    const geoTrigger = document.getElementById('geo-trigger');
    const geoDropdown = document.getElementById('geo-dropdown');
    const geoSelectedText = document.getElementById('geo-selected-text');
    const geoCheckboxes = document.querySelectorAll('.geo-option input[type="checkbox"]');
    const btnAcceptGeo = document.getElementById('btn-accept-geo');
    const geoError = document.getElementById('geo-error');

    geoTrigger.addEventListener('click', (e) => {
        geoDropdown.classList.toggle('hidden');
    });

    // Close dropdown if clicked outside
    document.addEventListener('click', (e) => {
        if (!geoTrigger.contains(e.target) && !geoDropdown.contains(e.target)) {
            geoDropdown.classList.add('hidden');
        }
    });

    // Handle Checkbox Changes (Min 1, Max 10)
    geoCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            const checkedCount = document.querySelectorAll('.geo-option input[type="checkbox"]:checked').length;
            
            if (checkedCount > 10) {
                cb.checked = false; // Revert
                geoError.classList.remove('hidden');
            } else if (checkedCount === 0) {
                cb.checked = true; // Force at least 1
                geoError.classList.add('hidden');
            } else {
                geoError.classList.add('hidden');
            }
            updateGeoText();
        });
    });

    // Accept Button
    btnAcceptGeo.addEventListener('click', () => {
        geoDropdown.classList.add('hidden');
    });

    function updateGeoText() {
        const checked = document.querySelectorAll('.geo-option input[type="checkbox"]:checked');
        const container = document.getElementById('geo-selected-tags');
        container.innerHTML = ''; // Clear existing tags

        if (checked.length === 0) {
            container.innerHTML = '<span style="color: #94a3b8; font-size: 0.95rem;">Select geographies...</span>';
        } else {
            Array.from(checked).forEach(c => {
                const tag = document.createElement('span');
                tag.className = 'geo-tag';
                tag.textContent = c.value;
                container.appendChild(tag);
            });
        }
    }
    // Initialize text
    updateGeoText();

    // --- Dynamic Form Logic ---
    providerSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        if (val === 'Mock Data') {
            apiKeyInput.disabled = true;
            apiKeyInput.placeholder = "Enter API Key";
            apiKeyLabel.textContent = "API Key not required for Mock Data";
            apiKeyInput.value = "";
        } else {
            apiKeyInput.disabled = false;
            apiKeyInput.placeholder = `Enter your ${val} API Key`;
            apiKeyLabel.textContent = `${val} API Key *`;
        }
    });

    // --- Form Submission ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Hide errors
        errorMsg.classList.add('hidden');
        errorMsg.textContent = "";

        const provider = providerSelect.value;
        const apiKey = apiKeyInput.value.trim();

        if (provider !== 'Mock Data' && !apiKey) {
            showError(`${provider} API Key is required.`);
            return;
        }

        // Get Multi-select Geographies
        const geoChecked = document.querySelectorAll('.geo-option input[type="checkbox"]:checked');
        const geographies = Array.from(geoChecked).map(cb => cb.value);

        if (geographies.length === 0) {
            showError("Select at least one geography.");
            return;
        }

        const reqBody = {
            provider: provider,
            api_key: apiKey,
            market_input: {
                product_description: document.getElementById('product').value,
                industry_vertical: document.getElementById('industry').value,
                company_stage: document.getElementById('stage').value,
                geographies: geographies,
                target_persona: document.getElementById('persona').value,
                pricing_model: document.getElementById('pricing-model').value,
                avg_price: parseFloat(document.getElementById('avg-price').value),
                price_unit: document.getElementById('price-unit').value,
                custom_research: document.getElementById('custom-research').value || null
            }
        };

        // Show loading
        submitBtn.disabled = true;
        loadingOverlay.classList.remove('hidden');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reqBody)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || `Server error: ${response.status}`);
            }

            const report = await response.json();
            currentReport = report;
            renderReport(report, provider);

            // Switch views
            formSection.classList.add('hidden');
            reportSection.classList.remove('hidden');

        } catch (err) {
            showError(err.message);
        } finally {
            submitBtn.disabled = false;
            loadingOverlay.classList.add('hidden');
        }
    });

    btnBack.addEventListener('click', () => {
        reportSection.classList.add('hidden');
        formSection.classList.remove('hidden');
        currentReport = null;
    });

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
    }

    // --- Tab Logic ---
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.add('hidden'));

            btn.classList.add('active');
            const target = document.getElementById(btn.dataset.target);
            target.classList.remove('hidden');

            // Force resize plots so they fit the container if they were hidden
            window.dispatchEvent(new Event('resize'));
        });
    });

    // --- Render Logic ---
    function formatCurrency(val) {
        if (val >= 1000000) return `$${(val/1000000).toFixed(1)}T`;
        if (val >= 1000) return `$${(val/1000).toFixed(1)}B`;
        return `$${Math.round(val)}M`;
    }

    function renderReport(report, provider) {
        document.getElementById('report-title').textContent = (provider !== 'Mock Data' && report.title) ? report.title : "TAM / SAM / SOM Analysis Overview";
        document.getElementById('r-investor-narrative').textContent = report.investor_narrative;
        
        const confSpan = document.getElementById('r-confidence-val');
        confSpan.textContent = report.confidence_rating;
        const confDiv = document.getElementById('r-confidence');
        confDiv.className = `confidence-badge mb-24 conf-${report.confidence_rating}`;

        // KPIs
        const updateKPI = (prefix, data) => {
            document.getElementById(`${prefix}-mid`).textContent = formatCurrency(data.mid);
            document.getElementById(`${prefix}-low`).textContent = `Low: ${formatCurrency(data.low)}`;
            document.getElementById(`${prefix}-high`).textContent = `High: ${formatCurrency(data.high)}`;
        };
        updateKPI('r-tam', report.reconciled_tam);
        updateKPI('r-sam', report.reconciled_sam);
        updateKPI('r-som', report.reconciled_som);

        // Overview
        document.getElementById('r-exec-summary').textContent = report.executive_summary;
        renderFunnelPlot(report);
        renderScenariosPlot(report);

        // Methodologies
        const methodsContainer = document.getElementById('methods-container');
        methodsContainer.innerHTML = '';
        report.methodology_results.forEach(mr => {
            let html = `
                <div class="method-box card fade-in">
                    <h3>🔬 ${mr.methodology} Approach</h3>
                    <p class="method-desc">${mr.narrative}</p>
                    <div class="metrics-row">
                        <div class="metric-mini"><label>TAM</label><div class="val">${formatCurrency(mr.tam.mid)}</div><div class="high">High: ${formatCurrency(mr.tam.high)}</div></div>
                        <div class="metric-mini"><label>SAM</label><div class="val">${formatCurrency(mr.sam.mid)}</div><div class="high">High: ${formatCurrency(mr.sam.high)}</div></div>
                        <div class="metric-mini"><label>SOM</label><div class="val">${formatCurrency(mr.som.mid)}</div><div class="high">High: ${formatCurrency(mr.som.high)}</div></div>
                    </div>
            `;
            if (mr.key_assumptions && mr.key_assumptions.length > 0) {
                html += `<strong>Key Assumptions</strong>`;
                mr.key_assumptions.forEach(a => {
                    const cColor = a.confidence === 'High' ? '#16A34A' : (a.confidence === 'Medium' ? '#D97706' : '#DC2626');
                    html += `
                        <div class="assumption-row">
                            <strong>${a.label}:</strong> ${a.value} &nbsp;&middot;&nbsp; 
                            <span style="color:#64748B">Source: ${a.source}</span> &nbsp;&middot;&nbsp; 
                            <span style="color:${cColor}; font-weight:600;">${a.confidence}</span>
                        </div>
                    `;
                });
            }
            html += `</div>`;
            methodsContainer.innerHTML += html;
        });
        renderMethodsPlot(report);

        // Projections
        const projTbody = document.querySelector('#proj-table tbody');
        projTbody.innerHTML = '';
        report.five_year_projection.forEach(p => {
            projTbody.innerHTML += `
                <tr>
                    <td>${p.year}</td>
                    <td>${formatCurrency(p.tam)}</td>
                    <td>${formatCurrency(p.sam)}</td>
                    <td style="font-weight:700; color:#16A34A;">${formatCurrency(p.som)}</td>
                    <td>${(p.cagr_applied).toFixed(1)}%</td>
                </tr>
            `;
        });
        renderProjectionPlot(report);

        // Sensitivity
        const sensContainer = document.getElementById('sens-container');
        sensContainer.innerHTML = '';
        report.sensitivity_axes.forEach((axis, idx) => {
            sensContainer.innerHTML += `
                <div class="col-half">
                    <div class="card mb-16">
                        <h4>${axis.variable}</h4>
                        <div id="plot-sens-${idx}" style="height: 250px;"></div>
                    </div>
                </div>
            `;
        });
        // wait a tick for DOM to update
        setTimeout(() => {
            report.sensitivity_axes.forEach((axis, idx) => renderSensitivityPlot(axis, `plot-sens-${idx}`));
        }, 50);

        // Risks
        const risksContainer = document.getElementById('risks-container');
        risksContainer.innerHTML = '';
        report.key_risks.forEach((risk, i) => {
            risksContainer.innerHTML += `<div class="risk-box"><strong>Risk ${i+1}:</strong> ${risk}</div>`;
        });

        // Sources
        const wbList = document.getElementById('wb-sources-list');
        wbList.innerHTML = '';
        if (report.world_bank_data_used && report.world_bank_data_used.length > 0) {
            report.world_bank_data_used.forEach(s => wbList.innerHTML += `<li>${s}</li>`);
        } else {
            wbList.innerHTML = `<li>None</li>`;
        }
        document.getElementById('ai-provider-name').textContent = provider;
        if (document.getElementById('custom-research').value) {
            document.getElementById('user-source-li').classList.remove('hidden');
        } else {
            document.getElementById('user-source-li').classList.add('hidden');
        }
    }

    // --- Plotly Charts ---
    const chartConfig = { responsive: true, displayModeBar: false };
    const layoutDefaults = {
        font: { family: "Inter, system-ui", color: "#1E293B" },
        paper_bgcolor: "white", plot_bgcolor: "white",
        margin: { l: 40, r: 20, t: 40, b: 40 }
    };

    function renderFunnelPlot(report) {
        // Simplified area chart mimicking the Streamlit streamgraph
        const xLabels = ["TAM", "SAM", "SOM"];
        
        const traceHigh = {
            x: xLabels, y: [report.reconciled_tam.high, report.reconciled_sam.high, report.reconciled_som.high],
            fill: 'tozeroy', mode: 'lines+markers', name: 'High Scenario',
            line: { color: '#E0E7FF', shape: 'spline' }, marker: { color: '#4F46E5' }
        };
        const traceMid = {
            x: xLabels, y: [report.reconciled_tam.mid, report.reconciled_sam.mid, report.reconciled_som.mid],
            fill: 'tozeroy', mode: 'lines+markers', name: 'Mid Scenario',
            line: { color: '#818CF8', shape: 'spline' }
        };
        const traceLow = {
            x: xLabels, y: [report.reconciled_tam.low, report.reconciled_sam.low, report.reconciled_som.low],
            fill: 'tozeroy', mode: 'lines+markers', name: 'Low Scenario',
            line: { color: '#4F46E5', shape: 'spline' }
        };

        const layout = { ...layoutDefaults, title: "Market Funnel — Scenario Ranges", yaxis: { showgrid: true, gridcolor: "#E2E8F0" } };
        Plotly.newPlot('plot-funnel', [traceHigh, traceMid, traceLow], layout, chartConfig);
    }

    function renderScenariosPlot(report) {
        const cats = ["TAM", "SAM", "SOM"];
        const high_vals = [report.reconciled_tam.high, report.reconciled_sam.high, report.reconciled_som.high];
        const mid_vals = [report.reconciled_tam.mid, report.reconciled_sam.mid, report.reconciled_som.mid];
        const low_vals = [report.reconciled_tam.low, report.reconciled_sam.low, report.reconciled_som.low];

        const tHigh = { x: cats, y: high_vals, type: 'bar', name: 'High Scenario', marker: { color: '#D4F234' }, text: high_vals.map(formatCurrency), textposition: 'auto' };
        const tMid = { x: cats, y: mid_vals, type: 'bar', name: 'Mid Scenario', marker: { color: '#84CC16' }, text: mid_vals.map(formatCurrency), textposition: 'auto' };
        const tLow = { x: cats, y: low_vals, type: 'bar', name: 'Low Scenario', marker: { color: '#334155' }, text: low_vals.map(formatCurrency), textposition: 'auto' };

        const layout = { ...layoutDefaults, title: "Scenario Analysis", barmode: 'group' };
        Plotly.newPlot('plot-scenarios', [tHigh, tMid, tLow], layout, chartConfig);
    }

    function renderMethodsPlot(report) {
        const methods = report.methodology_results.map(m => m.methodology);
        const tamVals = report.methodology_results.map(m => m.tam.mid);
        const samVals = report.methodology_results.map(m => m.sam.mid);
        const somVals = report.methodology_results.map(m => m.som.mid);

        const tTam = { x: methods, y: tamVals, type: 'bar', name: 'TAM', marker: { color: '#1F3C6B' }, text: tamVals.map(formatCurrency), textposition: 'auto' };
        const tSam = { x: methods, y: samVals, type: 'bar', name: 'SAM', marker: { color: '#4F46E5' }, text: samVals.map(formatCurrency), textposition: 'auto' };
        const tSom = { x: methods, y: somVals, type: 'bar', name: 'SOM', marker: { color: '#16A34A' }, text: somVals.map(formatCurrency), textposition: 'auto' };

        const layout = { ...layoutDefaults, title: "Methodology Comparison", barmode: 'group' };
        Plotly.newPlot('plot-methods', [tTam, tSam, tSom], layout, chartConfig);
    }

    function renderProjectionPlot(report) {
        const years = report.five_year_projection.map(p => p.year);
        const tamVals = report.five_year_projection.map(p => p.tam);
        const samVals = report.five_year_projection.map(p => p.sam);
        const somVals = report.five_year_projection.map(p => p.som);

        const tTam = { x: years, y: tamVals, mode: 'lines+markers+text', name: 'TAM', line: { color: '#1F3C6B', width: 3 }, marker: { size: 8 }, text: tamVals.map(formatCurrency), textposition: 'top center' };
        const tSam = { x: years, y: samVals, mode: 'lines+markers+text', name: 'SAM', line: { color: '#4F46E5', width: 3 }, marker: { size: 8 }, text: samVals.map(formatCurrency), textposition: 'top center' };
        const tSom = { x: years, y: somVals, mode: 'lines+markers+text', name: 'SOM', line: { color: '#16A34A', width: 3 }, marker: { size: 8 }, text: somVals.map(formatCurrency), textposition: 'top center' };

        const layout = { ...layoutDefaults, title: "5-Year Market Size Projection", xaxis: { type: 'category' } };
        Plotly.newPlot('plot-projection', [tTam, tSam, tSom], layout, chartConfig);
    }

    function renderSensitivityPlot(axis, divId) {
        // Base color for bars matching the light purple in the reference image
        const baseColor = '#DED7F6';
        const highlightColor = '#8A7BBF'; // Darker purple for max impact

        // Highlight the bar with the highest impact
        const maxVal = Math.max(...axis.som_impacts);
        const colors = axis.som_impacts.map(v => v === maxVal ? highlightColor : baseColor);

        const trace = {
            x: axis.values, 
            y: axis.som_impacts, 
            type: 'bar',
            name: 'SOM Impact', // Added for legend
            marker: { 
                color: colors,
                cornerradius: 8 // Works in newer Plotly versions for rounded tops
            },
            text: axis.som_impacts.map(formatCurrency), // Display text values
            textposition: 'outside',                    // Place text on top of bars
            textfont: { color: '#64748B', size: 11 },
            hoverinfo: 'y',
            hovertemplate: '<b>%{x}</b><br>Impact: %{y:$,.0f}M<extra></extra>',
            hoverlabel: {
                bgcolor: '#262626', // Dark tooltip
                bordercolor: '#262626',
                font: { color: 'white', family: 'Inter' }
            }
        };

        const layout = { 
            ...layoutDefaults, 
            margin: { l: 10, r: 10, t: 40, b: 30 }, // Increased top margin for text/legend
            showlegend: true, // Show legend
            legend: { 
                orientation: 'h', 
                y: 1.2, 
                x: 0, 
                font: { color: '#64748B' },
                itemclick: false,
                itemdoubleclick: false
            },
            xaxis: {
                showgrid: false,
                zeroline: false,
                showline: false,
                tickfont: { color: '#64748B', size: 12 },
                fixedrange: true
            },
            yaxis: {
                showgrid: false,
                zeroline: false,
                showline: false,
                showticklabels: false, // Clean look without Y-axis labels
                fixedrange: true,
                // Automatically increase range slightly to fit text
                range: [0, maxVal * 1.25] 
            },
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            hovermode: 'closest'
        };

        Plotly.newPlot(divId, [trace], layout, { displayModeBar: false, responsive: true });
    }

    // --- Exports ---
    const exportBtns = document.querySelectorAll('.btn-export');
    exportBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            if (!currentReport) return;
            const fmt = e.target.dataset.fmt;
            
            e.target.classList.add('loading');
            e.target.textContent = 'Generating...';

            try {
                const res = await fetch('/api/export', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ format: fmt, report: currentReport })
                });

                if (!res.ok) {
                    throw new Error("Export failed");
                }

                // Create a blob and trigger download
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                // Get filename from Content-Disposition header if possible, else default
                const cd = res.headers.get('Content-Disposition');
                let filename = `market_sizing.${fmt === 'powerpoint' ? 'pptx' : (fmt === 'excel' ? 'xlsx' : fmt)}`;
                if (cd && cd.includes('filename="')) {
                    filename = cd.split('filename="')[1].split('"')[0];
                }
                
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                
            } catch (err) {
                alert(err.message);
            } finally {
                e.target.classList.remove('loading');
                // Reset text
                if(fmt === 'json') e.target.textContent = 'JSON';
                if(fmt === 'excel') e.target.textContent = 'Excel';
                if(fmt === 'pdf') e.target.textContent = 'PDF';
                if(fmt === 'powerpoint') e.target.textContent = 'PowerPoint';
            }
        });
    });

});

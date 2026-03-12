/**
 * Solana Sniper Bot Dashboard
 * Real-time updates and visualization
 */

// Dashboard State
const state = {
    stats: {
        scanned: 0,
        filtered: 0,
        inferred: 0,
        safetyChecked: 0,
        safetyFailed: 0,
        trades: 0,
        successful: 0,
        balance: 0,
        available: 0
    },
    positions: [],
    activities: [],
    signals: [],
    chartData: {
        labels: [],
        scanned: [],
        filtered: [],
        trades: []
    }
};

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    startDataPolling();
    updateTime();
    setInterval(updateTime, 1000);
});

// Initialize Chart
function initChart() {
    const ctx = document.getElementById('activityChart').getContext('2d');
    
    // Generate initial empty data (last 60 minutes)
    const now = new Date();
    for (let i = 59; i >= 0; i--) {
        const time = new Date(now - i * 60000);
        state.chartData.labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        state.chartData.scanned.push(0);
        state.chartData.filtered.push(0);
        state.chartData.trades.push(0);
    }
    
    window.activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: state.chartData.labels,
            datasets: [
                {
                    label: 'Scanned',
                    data: state.chartData.scanned,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Filtered',
                    data: state.chartData.filtered,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Trades',
                    data: state.chartData.trades,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#9ca3af',
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1f2e',
                    titleColor: '#f9fafb',
                    bodyColor: '#9ca3af',
                    borderColor: '#2d3748',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#2d3748',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b7280',
                        maxTicksLimit: 8
                    }
                },
                y: {
                    grid: {
                        color: '#2d3748',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b7280'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

// Start Data Polling (simulated for now)
function startDataPolling() {
    // Poll every 5 seconds for updates
    setInterval(fetchData, 5000);
    
    // Initial fetch
    fetchData();
}

// Fetch Data from API (simulated)
async function fetchData() {
    try {
        // In production, this would fetch from your bot's API
        // const response = await fetch('/api/stats');
        // const data = await response.json();
        
        // For dry-run testing, simulate data
        simulateDataUpdate();
        
    } catch (error) {
        console.error('Failed to fetch data:', error);
    }
}

// Simulate Data Updates (for dry run testing)
function simulateDataUpdate() {
    // Randomly increment stats
    if (Math.random() > 0.3) {
        state.stats.scanned += Math.floor(Math.random() * 5) + 1;
    }
    
    if (Math.random() > 0.7) {
        state.stats.filtered += 1;
    }
    
    if (Math.random() > 0.85) {
        state.stats.inferred += 1;
        
        // Add to signals
        addSignal({
            token: generateTokenAddress(),
            confidence: (Math.random() * 0.3 + 0.7).toFixed(2),
            score: (Math.random() * 0.2 + 0.8).toFixed(2),
            age: Math.floor(Math.random() * 30)
        });
    }
    
    if (Math.random() > 0.9) {
        state.stats.safetyChecked += 1;
        
        if (Math.random() > 0.8) {
            state.stats.safetyFailed += 1;
            addActivity('warning', 'Safety check blocked suspicious token');
        }
    }
    
    if (Math.random() > 0.92) {
        state.stats.trades += 1;
        state.stats.successful += 1;
        
        addActivity('buy', `Executed dry-run buy order`);
        
        // Add to positions
        addPosition({
            token: generateTokenAddress(),
            entry: (Math.random() * 0.001).toFixed(6),
            size: (Math.random() * 0.05 + 0.01).toFixed(3),
            pnl: 0,
            status: 'OPEN'
        });
    }
    
    // Update chart data
    updateChartData();
    
    // Update UI
    updateStats();
}

// Update Chart Data
function updateChartData() {
    const now = new Date();
    const timeLabel = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    // Shift data
    state.chartData.labels.shift();
    state.chartData.labels.push(timeLabel);
    
    state.chartData.scanned.shift();
    state.chartData.scanned.push(state.stats.scanned);
    
    state.chartData.filtered.shift();
    state.chartData.filtered.push(state.stats.filtered);
    
    state.chartData.trades.shift();
    state.chartData.trades.push(state.stats.trades);
    
    // Update chart
    if (window.activityChart) {
        window.activityChart.update('none'); // 'none' for smooth animation
    }
}

// Update Stats Display
function updateStats() {
    // Animate number changes
    animateValue('scanned-count', parseInt(document.getElementById('scanned-count').textContent), state.stats.scanned);
    animateValue('filtered-count', parseInt(document.getElementById('filtered-count').textContent), state.stats.filtered);
    animateValue('inferred-count', parseInt(document.getElementById('inferred-count').textContent), state.stats.inferred);
    animateValue('safety-count', parseInt(document.getElementById('safety-count').textContent), state.stats.safetyChecked);
    animateValue('trades-count', parseInt(document.getElementById('trades-count').textContent), state.stats.trades);
    
    // Update percentages
    if (state.stats.scanned > 0) {
        const filterRate = ((state.stats.filtered / state.stats.scanned) * 100).toFixed(1);
        document.getElementById('filter-rate').textContent = `${filterRate}%`;
    }
    
    if (state.stats.safetyChecked > 0) {
        const blocked = state.stats.safetyFailed;
        document.getElementById('safety-fail').textContent = `${blocked} blocked`;
    }
    
    if (state.stats.trades > 0) {
        const successRate = ((state.stats.successful / state.stats.trades) * 100).toFixed(0);
        document.getElementById('success-rate').textContent = `${successRate}% success`;
    }
    
    // Update positions count
    document.getElementById('positions-count').textContent = state.positions.length;
}

// Animate Number Value
function animateValue(id, start, end) {
    if (start === end) return;
    
    const duration = 500;
    const startTime = performance.now();
    const element = document.getElementById(id);
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (end - start) * easeOut);
        
        element.textContent = current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Add Activity
function addActivity(type, message) {
    const activity = {
        type,
        message,
        time: new Date().toLocaleTimeString()
    };
    
    state.activities.unshift(activity);
    if (state.activities.length > 20) state.activities.pop();
    
    renderActivities();
    showToast(type, message);
}

// Render Activities
function renderActivities() {
    const container = document.getElementById('activity-list');
    
    container.innerHTML = state.activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon ${activity.type}">
                <i class="fas fa-${getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-info">
                <p>${activity.message}</p>
                <span class="time">${activity.time}</span>
            </div>
        </div>
    `).join('');
}

// Get Activity Icon
function getActivityIcon(type) {
    const icons = {
        scan: 'search',
        buy: 'arrow-down',
        sell: 'arrow-up',
        filter: 'filter',
        warning: 'exclamation-triangle',
        success: 'check',
        error: 'times'
    };
    return icons[type] || 'circle';
}

// Add Signal
function addSignal(signal) {
    state.signals.unshift(signal);
    if (state.signals.length > 10) state.signals.pop();
    
    renderSignals();
}

// Render Signals
function renderSignals() {
    const container = document.getElementById('top-signals');
    
    if (state.signals.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-chart-line"></i>
                <p>Waiting for high-confidence signals...</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.signals.map(signal => `
        <div class="token-item">
            <div class="token-info">
                <div class="token-icon">${signal.token.slice(0, 2)}</div>
                <div class="token-details">
                    <h4>${signal.token.slice(0, 8)}...</h4>
                    <span>${signal.age}s old • Score: ${signal.score}</span>
                </div>
            </div>
            <div class="token-metrics">
                <div class="confidence">${(signal.confidence * 100).toFixed(0)}%</div>
                <div class="score">confidence</div>
            </div>
        </div>
    `).join('');
}

// Add Position
function addPosition(position) {
    state.positions.unshift(position);
    renderPositions();
}

// Render Positions
function renderPositions() {
    const tbody = document.getElementById('positions-table');
    
    if (state.positions.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-state">
                <td colspan="5">No active positions</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = state.positions.map(pos => `
        <tr>
            <td><strong>${pos.token.slice(0, 8)}...</strong></td>
            <td>$${pos.entry}</td>
            <td>${pos.size} SOL</td>
            <td class="${pos.pnl >= 0 ? 'positive' : 'negative'}">${pos.pnl >= 0 ? '+' : ''}${pos.pnl}%</td>
            <td><span class="status-badge ${pos.status.toLowerCase()}">${pos.status}</span></td>
        </tr>
    `).join('');
}

// Show Toast Notification
function showToast(type, message) {
    const container = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas fa-${getActivityIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Generate Random Token Address
function generateTokenAddress() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 44; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// Update Time Display
function updateTime() {
    // Could add a clock element if needed
}

// Handle Time Range Buttons
document.querySelectorAll('.btn-time').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.btn-time').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        // In production, this would fetch different time range data
        showToast('info', `Switched to ${e.target.textContent} view`);
    });
});

// Handle Clear Activity Button
document.querySelector('.btn-clear')?.addEventListener('click', () => {
    state.activities = [];
    renderActivities();
    showToast('info', 'Activity log cleared');
});

// Simulate initial activity
setTimeout(() => {
    addActivity('scan', 'Bot started scanning DEX Screener');
    addActivity('info', 'Connected to Solana mainnet');
}, 1000);

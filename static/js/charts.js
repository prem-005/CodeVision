// ===== CodeVision - Dashboard Charts System =====

document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/dashboard')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.stats) {
                initDashboardCharts(data.stats);
            }
        })
        .catch(err => {
            console.log('Error loading dashboard stats:', err);
        });
});

function initDashboardCharts(stats) {
    if (typeof Chart === 'undefined') return;

    // Chart.js dark theme defaults
    Chart.defaults.color = '#7d8590';
    Chart.defaults.borderColor = '#30363d';
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

    // 1. Problems Solved Over Time (Line)
    const timeCtx = document.getElementById('chartSolvedTime');
    if (timeCtx) {
        const timeData = stats.solved_over_time || { labels: ['Day 1'], data: [0] };
        new Chart(timeCtx, {
            type: 'line',
            data: {
                labels: timeData.labels,
                datasets: [{
                    label: 'Solved Problems',
                    data: timeData.data,
                    borderColor: '#f97316',
                    backgroundColor: 'rgba(249, 115, 22, 0.12)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2,
                    pointBackgroundColor: '#f97316',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    }

    // 2. Difficulty Breakdown (Doughnut)
    const diffCtx = document.getElementById('chartDifficulty');
    if (diffCtx) {
        const diffData = stats.difficulty_breakdown || { 'Easy': stats.easy_solved || 0, 'Medium': stats.medium_solved || 0, 'Hard': stats.hard_solved || 0 };
        new Chart(diffCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(diffData),
                datasets: [{
                    data: Object.values(diffData),
                    backgroundColor: ['#3fb850', '#d29922', '#f85149'],
                    borderWidth: 2,
                    borderColor: '#161b22',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#e6edf3', boxWidth: 12, padding: 16 }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 3. Topic Performance (Bar)
    const topicCtx = document.getElementById('chartTopicPerformance');
    if (topicCtx) {
        const topicData = stats.topic_breakdown || { 'Arrays': 0, 'Strings': 0, 'DP': 0 };
        new Chart(topicCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(topicData),
                datasets: [{
                    label: 'Problems Solved',
                    data: Object.values(topicData),
                    backgroundColor: '#58a6ff',
                    borderRadius: 4,
                    maxBarThickness: 32
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }

    // 4. Submission Verdict Distribution (Doughnut)
    const accCtx = document.getElementById('chartAccuracy');
    if (accCtx) {
        const verdictData = stats.verdict_breakdown || { 'Accepted': 0, 'Wrong Answer': 0 };
        new Chart(accCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(verdictData),
                datasets: [{
                    data: Object.values(verdictData),
                    backgroundColor: ['#3fb850', '#f85149', '#d29922', '#bc8cff'],
                    borderWidth: 2,
                    borderColor: '#161b22'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#e6edf3', boxWidth: 12, padding: 16 }
                    }
                },
                cutout: '68%'
            }
        });
    }
}

// Radar Chart helper if present
function renderSkillRadarChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === 'undefined') return;

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Skill Proficiency (%)',
                data: data,
                backgroundColor: 'rgba(249, 115, 22, 0.2)',
                borderColor: '#f97316',
                pointBackgroundColor: '#f97316',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    angleLines: { color: '#30363d' },
                    grid: { color: '#30363d' },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: { color: '#7d8590', backdropColor: 'transparent' },
                    pointLabels: { color: '#e6edf3', font: { size: 11, weight: '600' } }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

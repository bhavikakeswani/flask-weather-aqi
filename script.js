const ctx = document.getElementById('rainChart').getContext('2d');
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['10AM','11AM','12PM','1PM','2PM','3PM'],
    datasets: [{
      label: 'Rain %',
      data: [20, 50, 80, 60, 40, 30],
      borderColor: '#29B6F6',
      backgroundColor: 'rgba(41,182,246,0.3)',
      fill: true,
      tension: 0.4
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, ticks: { stepSize: 20 } }
    }
  }
});

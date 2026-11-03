new Chart(ctx, {
  type: "doughnut",
  data: {
    labels: ["Google Ads", "Organic", "Referrals", "Social", "Email"],
    datasets: [{ data: [86, 54, 31, 22, 11],
      backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"] }]
  },
  options: { plugins: { title: { display: true, text: "Lead Sources Breakdown 🚀" },
                        legend: { display: true, position: "right" } } }
});

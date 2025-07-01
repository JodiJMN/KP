document.addEventListener("DOMContentLoaded", function () {
  const salesChart = new ApexCharts(document.querySelector("#sales-chart"), {
    series: [
      { name: "Digital Goods", data: [28, 48, 40, 19, 86, 27, 90] },
      { name: "Electronics", data: [65, 59, 80, 81, 56, 55, 40] }
    ],
    chart: { type: "area", height: 180 },
    dataLabels: { enabled: false },
    stroke: { curve: "smooth" },
    xaxis: {
      type: "datetime",
      categories: [
        "2023-01-01", "2023-02-01", "2023-03-01",
        "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01"
      ]
    }
  });
  salesChart.render();
});

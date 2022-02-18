const plotChart = (result) => {
  const ctx = document.getElementById("evolutionChart").getContext("2d");

  const firstYear = new Date(result[0].date).getFullYear();

  const data = {
    labels: result.map((month) => {
      return new Date(month.date).toLocaleDateString();
    }),
    datasets: [
      {
        data: result.map((month) => ({
          t: new Date(month.date),
          y: month.total_value.toFixed(2),
        })),
        label: "Total Value",
        backgroundColor: "rgba(100, 153, 202, 0.4)",
      },
      {
        data: result.map((month) => ({
          t: new Date(month.date),
          y: month.invested_value.toFixed(2),
        })),
        label: "Invested Value",
        backgroundColor: "rgba(97, 216, 88, 0.4)",
      },
    ],
  };

  const myLineChart = new Chart(ctx, {
    type: "line",
    data,
    options: {
      scales: {
        xAxes: [
          {
            type: "time",
            time: {
              unit: "month",
              min: String(firstYear),
            },
          },
        ],
      },
    },
  });
};

$(document).ready(() => {
  console.log(_assets);
  plotChart(_assets);
});

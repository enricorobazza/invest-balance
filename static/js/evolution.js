const plotChart = (result) => {
  const ctx = document.getElementById("evolutionChart").getContext("2d");

  const data = {
    labels: result.map(month => {
      return new Date(month.date).toLocaleDateString()
    }),
    datasets: [
        {
            data: result.map(month => ({t: new Date(month.date), y: month.total_value})),
            label: "Total Value"
        },
        {
            data: result.map(month => ({t: new Date(month.date), y: month.invested_value})),
            label: "Invested Value"
        },

    ]
  };

  const myLineChart = new Chart(ctx, {
    type: 'line',
    data,
    options: {
      scales: {
          xAxes: [{
              type: 'time',
              time: {
                  unit: 'month'
              }
          }]
      }
    }
  });
}


$(document).ready(() => {
  console.log(_assets);
  plotChart(_assets);
})
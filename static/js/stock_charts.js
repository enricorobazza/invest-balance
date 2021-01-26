const plotChart = (result) => {
  const ctx = document.getElementById("historyChart").getContext("2d");

  const data = {
    // labels: new_categories.map(category => category.title),
    labels: result.prices.map(price => {
      console.log(new Date(price.date).toLocaleDateString());
      return new Date(price.date).toLocaleDateString()
      let date = price.date.substring(0,10).split("-");
      return date[2] + "/" + date[1] + "/" + date[0];
    }),
    datasets: [
        {
            // data: result.prices.map(price => price.value),
            data: result.prices.map(price => ({t: new Date(price.date), y: price.value})),
            label: result.code
            // data: new_categories.map(category => Math.round(category.current_value / patrimony * 10000)/100),
            // backgroundColor: new_categories.map((category, index) => colors[index%6])
        }]
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
  if(!code || code.trim() === "")
    code = "MGLU3.SA"
  $.ajax({
    url: `/history/${code}`,
    success: (result) => {
      plotChart(result);
    },
  });
})
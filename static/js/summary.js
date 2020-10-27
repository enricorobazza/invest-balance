const categories_count = categories.length;
let fetched_categories_count = 0;
let patrimony = initial_patrimony;

$('tbody tr[key="category"]').each(async (index, elem) => {
  const pk = parseInt($($(elem).find('td[key="pk"]')[0]).html())
  let category = categories.filter(c => c.pk === pk)[0];
  let promises = [];
  category.assets.forEach(async asset => {
    promises.push($.ajax({
      url: `/stock/${asset.code}`,
    }));
  });
  const response = await Promise.all(promises);
  let current_value = 0;
  response.forEach(asset => {
    current_value += asset.price * category.assets.filter(a => a.code == asset.code)[0].amount;
  })
  categories = categories.map((category) => {
    if(category.pk === pk){
      category.current_value = current_value;
    }
    return category;
  })
  const sum = parseFloat($($(elem).find('td[key="sum"]')[0]).html());
  $(elem).removeClass('bg-success');
  $(elem).removeClass('bg-danger');
  if(current_value >= sum) $(elem).addClass('bg-success');
  else $(elem).addClass('bg-danger');

  const yield = (current_value - sum)/sum * 100;

  $($(elem).find('td[key="current_value"]')[0]).html(current_value.toFixed(2));
  $($(elem).find('td[key="yield"]')[0]).html(yield.toFixed(2));

  patrimony += current_value;

  fetched_categories_count++;

  if(fetched_categories_count === categories_count){
    $($('tr[key="total"]').find('td[key="current_value"]')[0]).html(patrimony.toFixed(2));
    const total_sum = parseFloat($($('tr[key="total"]').find('td[key="sum"]')[0]).html());
    const patrimony_yield = (patrimony - total_sum)/total_sum * 100;
    $($('tr[key="total"]').find('td[key="yield"]')[0]).html(patrimony_yield.toFixed(2));

    const totalTr = $('tr[key="total"]')[0];
    $(totalTr).removeClass('bg-success');
    $(totalTr).removeClass('bg-danger');

    if(patrimony > total_sum) $(totalTr).addClass('bg-success');
    else $(totalTr).addClass('bg-danger');

    const colors = [
      "#878BB6", 
      "#4ACAB4", 
      "#FF8153", 
      "#FFEA88",
      "#3498db",
      "#2ecc71"
    ]

    const new_categories = categories.concat(savings)

    const data = {
      labels: new_categories.map(category => category.title),
      datasets: [
          {
              data: new_categories.map(category => Math.round(category.current_value / patrimony * 10000)/100),
              backgroundColor: new_categories.map((category, index) => colors[index%6])
          }]
    };

    const ctx = document.getElementById("summaryChart").getContext("2d");

    const myPieChart = new Chart(ctx, {
      type: 'pie',
      data,
    });
  }
})



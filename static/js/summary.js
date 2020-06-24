const categories_count = categories.length;
let fetched_categories_count = 0;
let patrimony = savings_current_value;

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
  const sum = parseFloat($($(elem).find('td[key="sum"]')[0]).html());
  $(elem).removeClass('bg-success');
  $(elem).removeClass('bg-danger');
  if(current_value >= sum) $(elem).addClass('bg-success');
  else $(elem).addClass('bg-danger');

  const yield = (current_value - sum)/current_value * 100;

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
  }
})
$('tbody tr').each((index, elem) => {
  let code = $($(elem).find('td[key="code"]')[0]).html();
  $.ajax({
    url: `/stock/${code}`,
    success: (result) => {
      $($(elem).find('td[key="current_value"]')[0]).html(result.price);
      const paid_value = parseFloat($($(elem).find('td[key="paid_value"]')[0]).html());
      const current_value = parseFloat(result.price);
      const amount = parseFloat($($(elem).find('td[key="amount"]')[0]).html());
      const yield = (current_value - paid_value) / paid_value * 100;
      $($(elem).find('td[key="yield"]')[0]).html(yield.toFixed(2));

      const profit_per_share = current_value - paid_value;
      $($(elem).find('td[key="profit_per_share"]')[0]).html(profit_per_share.toFixed(2));

      const total_profit = profit_per_share * amount;
      $($(elem).find('td[key="total_profit"]')[0]).html(total_profit.toFixed(2));

      $(elem).removeClass('bg-success');
      $(elem).removeClass('bg-danger');

      if(current_value > paid_value) $(elem).addClass('bg-success');
      else if(current_value < paid_value) $(elem).addClass('bg-danger');
    },
  });
});

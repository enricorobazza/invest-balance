let promise_count = 0;
const assets_count = $('tbody tr').length;

function sortTable() {
  var table, rows, switching, i, x, y, shouldSwitch;
  table = document.getElementById("assets");
  switching = true;
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = parseFloat($(rows[i]).find('td[key="yield"]').html())
      y = parseFloat($(rows[i+1]).find('td[key="yield"]').html())
      // Check if the two rows should switch place:
      if (x < y) {
        // If so, mark as a switch and break the loop:
        shouldSwitch = true;
        break;
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
    }
  }
}

$('tbody tr').each((index, elem) => {
  let code = $($(elem).find('td[key="code"]')[0]).html();
  let invest_type = $($(elem).find('td[key="invest_type"]')[0]).html();
  const url = invest_type === 'S' ? 'stock' : 'fund';
  
  $.ajax({
    url: `/${url}/${code}`,
    success: (result) => {
      promise_count++;
      $($(elem).find('td[key="price"]')[0]).html(result.price);
      const cost_avg = parseFloat($($(elem).find('td[key="cost_avg"]')[0]).html());
      const price = parseFloat(result.price);
      if(cost_avg > 0){
        if(price > cost_avg) $(elem).addClass('bg-success');
        else if(price < cost_avg) $(elem).addClass('bg-danger');

        let yield = (price - cost_avg) / cost_avg * 100;
        $($(elem).find('td[key="yield"]')[0]).html(yield.toFixed(2));
      }

      if(promise_count == assets_count){
        sortTable()
      }
    },
  });
});

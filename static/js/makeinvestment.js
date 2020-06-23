let promise_count = 0;
const assets_count = $('tbody tr').length;
let patrimony = 0;

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
      x = parseFloat($(rows[i]).find('td[key="to_invest"]').html())
      y = parseFloat($(rows[i+1]).find('td[key="to_invest"]').html())
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
  $.ajax({
    url: `/stock/${code}`,
    success: (result) => {
      promise_count++;
      $($(elem).find('td[key="price"]')[0]).html(result.price);
      const price = parseFloat(result.price);
      const count = $($(elem).find('td[key="count"]')[0]).html();
      const have = price * count;
      $($(elem).find('td[key="have"]')[0]).html(have.toFixed(2));
      patrimony += have;

      if(promise_count == assets_count){
        $('tbody tr').each((index, elem) => {
          const _have = parseFloat($($(elem).find('td[key="have"]')[0]).html());
          const have_percentage = _have / patrimony * 100;
          $($(elem).find('td[key="have_percentage"]')[0]).html(have_percentage.toFixed(2));
          const ideal_percentage = parseFloat($($(elem).find('td[key="ideal_percentage"]')[0]).html())
          if(have_percentage > ideal_percentage) $(elem).addClass('bg-danger');
          else $(elem).addClass('bg-success');

          const to_invest = ideal_percentage / 100 * patrimony - _have;
          $($(elem).find('td[key="to_invest"]')[0]).html(to_invest.toFixed(2));
        });
        sortTable();
      }
    },
  });
});

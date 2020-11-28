let promise_count = 0;
const assets_count = $('tbody tr[key="asset"]').length;
let global_patrimony = initial_patrimony;
let stepOpen = false;

function sortTable() {
  var table, rows, switching, i, x, y, shouldSwitch;
  table = document.getElementById('assets');
  switching = true;
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < rows.length - 1; i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = parseFloat($(rows[i]).find('td[key="to_invest"]').html());
      y = parseFloat(
        $(rows[i + 1])
          .find('td[key="to_invest"]')
          .html()
      );
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

const updatePercentages = (patrimony) => {
  $('tbody tr[key="asset"]').each((index, elem) => {
    const _price = parseFloat($($(elem).find('td[key="price"]')[0]).html());
    const _have = parseFloat($($(elem).find('td[key="have"]')[0]).html());
    const have_percentage = patrimony > 0 ? (_have / patrimony) * 100 : 0;
    $($(elem).find('td[key="have_percentage"]')[0]).html(
      have_percentage.toFixed(2)
    );
    const ideal_percentage = parseFloat(
      $($(elem).find('td[key="ideal_percentage"]')[0]).html()
    );
    $(elem).removeClass('bg-danger');
    $(elem).removeClass('bg-success');

    if (have_percentage > ideal_percentage) $(elem).addClass('bg-danger');
    else $(elem).addClass('bg-success');

    const to_invest = (ideal_percentage / 100) * patrimony - _have;
    const to_invest_count = to_invest / _price;

    $($(elem).find('td[key="to_invest"]')[0]).html(to_invest.toFixed(2));
    $($(elem).find('td[key="to_invest_count"]')[0]).html(
      to_invest_count.toFixed(2)
    );
  });

  // SAVINGS
  $('tbody tr[key="saving"]').each((index, elem) => {
    const have_saved = parseFloat(
      $($(elem).find('td[key="have"]')[0]).html()
    );
    const ideal_save_percentage = parseFloat(
      $($(elem).find('td[key="ideal_percentage"]')[0]).html()
    );
    const saved_percentage = (have_saved / patrimony) * 100;
    $($(elem).find('td[key="have_percentage"]')[0]).html(
      saved_percentage.toFixed(2)
    );

    const to_save = (ideal_save_percentage / 100) * patrimony - have_saved;
    $($(elem).find('td[key="to_invest"]')[0]).html(to_save.toFixed(2));
    
    $(elem).removeClass('bg-danger');
    $(elem).removeClass('bg-success');
  
    if (saved_percentage > ideal_save_percentage)
      $(elem).addClass('bg-danger');
    else $(elem).addClass('bg-success');
  });
  getDollarInvestments();
  sortTable();
};

const getPrices = () => {
  global_patrimony = initial_patrimony;
  $('tbody tr[key="asset"]').each((index, elem) => {
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
        global_patrimony += have;

        if (promise_count == assets_count) updatePercentages(global_patrimony);
      },
    });
  });
};

const getDollarInvestments = () => {
  $.ajax({
    url: `/dollarquote`,
    success: (result) => {
      $('tbody tr').each((index, elem) => {
        const to_invest = parseFloat($($(elem).find("td[key='to_invest']")[0]).html());
        const to_invest_dollar = to_invest / result.quote;
        $($(elem).find("td[key='to_invest_dollar']")[0]).html(to_invest_dollar.toFixed(2))
      });
    },
  });
}

getPrices();

$("#simulate_investment").on('submit', (e) => {
  e.preventDefault();
  simulated_investment = parseFloat($("#simulated_investment").val())
  if(isNaN(simulated_investment)) simulated_investment = 0;
  new_patrimony = global_patrimony + simulated_investment;
  updatePercentages(new_patrimony);
  $(".btnOpen").css("display", "inline-block");
  closeStepByStep();
})

$("#btnToInvestReal").click((e) => {
  e.preventDefault();
  $(".real").css('display', 'none');
  $(".dollar").css('display', 'table-cell');
})

$("#btnToInvestDollar").click((e) => {
  e.preventDefault();
  $(".real").css('display', 'table-cell');
  $(".dollar").css('display', 'none');
})

const closeStepByStep = () => {
  $("#stepByStep").css('display', "none")
  stepOpen = false;
  $(".btnOpen").html("Abrir Passo a Passo");
}

$(".btnOpen").click((e) => {
  e.preventDefault();
  if(stepOpen) {
    closeStepByStep();
    return;
  }
  $(".btnOpen").html("Fechar Passo a Passo");
  stepOpen = true;
  $("#stepByStep").css('display', "block")
  $(".stepper").html("");
  let money = parseFloat($("#simulated_investment").val());
  let assetIndex = 0;
  let categorySum = {};
  let total = 0;
  while(money > 0){
    const row = $("#assets").find("tr")[assetIndex+1];
    let to_invest = parseFloat($($(row).find("td[key='to_invest']")[0]).html())
    if(to_invest <= 0) break;
    let short_code = $($(row).find("td[key='short_code']")[0]).html()
    const category = $($(row).find("td[key='category']")[0]).html()
    const fractioned = $($(row).find("td[key='fractioned']")[0]).html() === "True" ? true : false;
    const price = parseFloat($($(row).find("td[key='price']")[0]).html())
    if(fractioned) {
      if(to_invest > money){
        to_invest = money;
      }
    }
    else{
      let to_invest_count = parseFloat($($(row).find("td[key='to_invest_count']")[0]).html())
      to_invest_count = Math.round(to_invest_count);
      to_invest = price * to_invest_count;
      while(to_invest > money){
        to_invest -= price;
      }
    }

    if(!short_code) short_code = category;

    let amount = price > 0 ? to_invest / price : 0;
    amount = amount.toFixed(4).replace(/0{0,2}$/, "");

    if(to_invest > 0) {
      $(".stepper").append(`<li>${assetIndex+1}º Passo: ${short_code}: R$ ${to_invest.toFixed(2)} (${amount})</li>`)
      if(categorySum[category]) categorySum[category] += to_invest
      else categorySum[category] = to_invest;
      total += to_invest;
      money -= to_invest;
    }
    assetIndex+= 1;
  }

  $(".stepper").append(`<hr />`)
  Object.entries(categorySum).forEach(([key, value]) => {
    $(".stepper").append(`<li>${key}: ${value.toFixed(2)}</li>`)
  })
  $(".stepper").append(`<hr />`)
  $(".stepper").append(`<li>Total: ${total.toFixed(2)}</li>`)
})
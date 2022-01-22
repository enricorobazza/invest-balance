const updateUrl = (newParam) => {
  const urlSearchParams = new URLSearchParams(window.location.search);
  let params = Object.fromEntries(urlSearchParams.entries());
  params = { ...params, ...newParam };

  let url = baseUrl;

  Object.keys(params).forEach((key) => {
    url += `${key}=${params[key]}&`;
  });

  url = url.substr(0, url.length - 1);

  window.location.href = url;
};

$("#startdate").datepicker({
  uiLibrary: "bootstrap4",
  value: startDate,
  locale: "pt-br",
  format: "dd/mm/yyyy",
});

$("#enddate").datepicker({
  uiLibrary: "bootstrap4",
  value: endDate,

  locale: "pt-br",
  format: "dd/mm/yyyy",
});

let enddate = $("#enddate").val();
let startdate = $("#startdate").val();

$("#startdate").change((e) => {
  e.preventDefault();
  if (startdate !== e.target.value) {
    updateUrl({ startdate: e.target.value });
  }
});

$("#enddate").change((e) => {
  e.preventDefault();
  if (enddate !== e.target.value) {
    updateUrl({ enddate: e.target.value });
  }
});

const filterTransactions = (category = "") => {
  $("#transactions tbody tr").hide();
  $("#transactions tbody tr").each((i, transaction) => {
    const _category = $(transaction)
      .find("td[key='category_name']")
      .first()
      .html()
      .trim();
    if (category == "" || _category == category) $(transaction).show();
  });
};

$("#categories td[key='category']").click((e) => {
  const category = $(e.target)
    .parent()
    .parent()
    .find("td[key='category_name']")
    .first()
    .html()
    .trim();
  const div = $("<div />");
  div.html($(e.target).parent().html());
  div.find("div").first().append("<i class='ml-2 fa fa-times'></i>");
  $("#filterCategory").html(div.html());
  filterTransactions(category);
  $("#filterCategory").click((e) => {
    $("#filterCategory").html("");
    filterTransactions();
    $("#collapseOne").collapse("show");
  });
  $("#collapseTwo").collapse("show");
});

$(document).ready(() => {
  const getParams = () => {
    const urlSearchParams = new URLSearchParams(window.location.search);
    return Object.fromEntries(urlSearchParams.entries());
  };

  const buildUrl = (params, _baseUrl = "") => {
    let url = _baseUrl == "" ? baseUrl : _baseUrl;

    Object.keys(params).forEach((key) => {
      if (params[key] != null && params[key] != "")
        url += `${key}=${params[key]}&`;
    });

    url = url.substr(0, url.length - 1);
    window.location.href = url;
  };

  const getN = (params) => {
    if (params.hasOwnProperty("n")) {
      return parseInt(params.n);
    }
    return 0;
  };

  $(".minus").click((e) => {
    e.preventDefault();
    let params = getParams();
    const n = getN(params) + 1;
    params["n"] = n;
    buildUrl(params);
  });

  $(".plus").click((e) => {
    e.preventDefault();
    let params = getParams();
    let n = getN(params) - 1;
    if (n < 0) return;
    params["n"] = n;
    buildUrl(params);
  });

  const updateUrl = (newParam, _baseUrl = "") => {
    let params = getParams();
    params = { ...params, ...newParam };
    buildUrl(params, _baseUrl);
  };

  $(".all").click((e) => {
    e.preventDefault();
    let params = getParams();
    if ("variable" in params) {
      delete params["variable"];
    }
    buildUrl(params);
  });

  $(".variable").click((e) => {
    e.preventDefault();
    updateUrl({ variable: "true" });
  });

  $(".refresh").click((e) => {
    e.preventDefault();
    updateUrl({}, refreshUrl);
  });

  $(".startdate").datepicker({
    uiLibrary: "bootstrap4",
    value:
      startDate ||
      moment(new Date()).tz("America/Sao_paulo").format("DD/MM/YYYY"),
    locale: "pt-br",
    format: "dd/mm/yyyy",
  });

  $(".enddate").datepicker({
    uiLibrary: "bootstrap4",
    value:
      endDate ||
      moment(new Date()).tz("America/Sao_paulo").format("DD/MM/YYYY"),
    locale: "pt-br",
    format: "dd/mm/yyyy",
  });

  let enddate = $(".enddate").val();
  let startdate = $(".startdate").val();

  $(".startdate").change((e) => {
    e.preventDefault();
    if (startdate !== e.target.value) {
      updateUrl({ startdate: e.target.value });
    }
  });

  $(".enddate").change((e) => {
    e.preventDefault();
    if (enddate !== e.target.value) {
      updateUrl({ enddate: e.target.value });
    }
  });

  const filterTransactions = (category = "") => {
    $(".transactions-table tbody tr.transaction-date").hide();

    const applyHide = (selector, hideFn, showFn, plusFn) => {
      hideFn($(`${selector}  tbody tr.transaction`));

      $(`${selector} tbody tr.transaction`).each((i, transaction) => {
        const _category = $(transaction)
          .find(".t-category-name")
          .first()
          .html()
          .trim();
        if (category == "" || _category == category) {
          showFn($(transaction));
          if (plusFn) plusFn(transaction);
        }
      });
    };

    applyHide(
      ".transactions-table",
      (el) => el.removeClass("d-flex").addClass("d-none"),
      (el) => el.removeClass("d-none").addClass("d-flex"),
      (transaction) => {
        const dateKey = $(transaction).attr("date-key");
        $(
          `.transactions-table tbody tr.transaction-date[key='${dateKey}']`
        ).show();
      }
    );

    applyHide(
      ".transactions-table-lg",
      (el) => el.hide(),
      (el) => el.show()
    );
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
    div.find("div").first().removeClass("m-2").addClass("ml-2");
    $(".filter-category").html(div.html());
    filterTransactions(category);
    $(".filter-category").click((e) => {
      $(".filter-category").html("");
      filterTransactions();
      $("#collapseOne").collapse("show");
    });
    $("#collapseTwo").collapse("show");
  });

  $(".ignore-input").click((e) => {
    const el = e.target;
    const tr = $(el).parent().parent().parent();
    const code = $(tr).find(".t-code").first().html();
    const params = getParams();
    let ignore = [];

    if ("ignore" in params) {
      ignore = params["ignore"].split(",");
    }

    const isIgnored = String($(e.target).parent().html()).includes(
      "fa-eye-slash"
    );

    if (!isIgnored) {
      ignore.push(code);
    } else {
      ignore = ignore.filter((val) => val != code);
    }

    updateUrl({ ignore: ignore.join(",") });
  });
});

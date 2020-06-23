$('tbody tr').each((index, elem) => {
  let code = $($(elem).find('td')[4]).html();
  console.log(elem);
  $.ajax({
    url: `/stock/${code}`,
    success: (result) => {
      $($(elem).find('td')[6]).html(result.price);
    },
  });
});

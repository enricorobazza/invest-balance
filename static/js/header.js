const path = window.location.pathname;

const summary = document.getElementById('summary');
const invest = document.getElementById('invest');


const clear = () => {
  summary.classList.remove('active');
  invest.classList.remove('active');
}

clear();

if(path.startsWith('/invest')){
  invest.classList.add('active');
}
else summary.classList.add('active');
const path = window.location.pathname;

const summary = document.getElementById("summary_header");
const assets = document.getElementById("assets_header");
const invest = document.getElementById("invest_header");
const history = document.getElementById("history_header");
const guiabolso = document.getElementById("guiabolso_header");
const risk = document.getElementById("risk_header");

const clear = () => {
  summary.classList.remove("active");
  assets.classList.remove("active");
  invest.classList.remove("active");
  history.classList.remove("active");
  risk.classList.remove("active");
  guiabolso.classList.remove("active");
};

clear();

if (path.startsWith("/invest")) invest.classList.add("active");
else if (path.startsWith("/assets")) assets.classList.add("active");
else if (path.startsWith("/history")) history.classList.add("active");
else if (path.startsWith("/risk")) risk.classList.add("active");
else if (path.startsWith("/guiabolso")) guiabolso.classList.add("active");
else if (path === "/") summary.classList.add("active");

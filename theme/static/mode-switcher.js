(function () {
  const html = document.documentElement;

  function getState() {
    return localStorage.getItem("theme") || "auto";
  }

  function applyState(state) {
    if (state === "auto") {
      html.removeAttribute("data-theme");
    } else {
      html.setAttribute("data-theme", state);
    }
  }

  function update() {
    const state = getState();
    document.querySelectorAll(".theme-option").forEach(function (btn) {
      btn.classList.toggle("active", btn.dataset.themeValue === state);
    });
  }

  document.querySelectorAll(".theme-option").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const value = btn.dataset.themeValue;
      if (value === "auto") {
        localStorage.removeItem("theme");
      } else {
        localStorage.setItem("theme", value);
      }
      applyState(value);
      update();
    });
  });

  applyState(getState());
  update();
})();

document.addEventListener("DOMContentLoaded", () => {
  let changed = false;

  form = document.querySelector("[data-aviso-cambios]");

  if (form) {
    form.addEventListener("change", () => (changed = true));
    form.addEventListener("submit", () => (changed = false));
  }

  window.addEventListener("beforeunload", (event) => {
    if (changed) {
      event.preventDefault();
      event.returnValue = "Tienes cambios sin guardar!";
    };
  });


  document.querySelectorAll('button[data-confirm]').forEach(button => {
    button.addEventListener("click", (event) => {
      const message = button.getAttribute("data-confirm") || "¿Estás seguro?";
      if (!confirm(message)) {
        event.preventDefault();
      }
    });
  });
  
});

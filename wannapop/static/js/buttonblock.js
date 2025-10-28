document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('[data-disable-on-submit]');

    if (!form) return;

    const bloquearBotton = (event) => {
        event.preventDefault();
        
        const searchButton = document.getElementById('buscar_btn');
        if (searchButton) {
            searchButton.disabled = true;
            searchButton.textContent = "Buscando";

            setTimeout(() => {

                searchButton.textContent = "Buscando.";
            }, 500);

            setTimeout(() => {

                searchButton.textContent = "Buscando..";
            }, 1000);

            setTimeout(() => {

                searchButton.textContent = "Buscando...";
            }, 1500);

            setTimeout(() => {
                searchButton.disabled = false;
                searchButton.textContent = "Buscar";
            }, 2000);
        }
    };

    form.addEventListener('submit', bloquearBotton);
});
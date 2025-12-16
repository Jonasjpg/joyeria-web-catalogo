document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("modal");
    const modalImg = document.getElementById("modal-img");
    const modalNombre = document.getElementById("modal-nombre");
    const modalMaterial = document.getElementById("modal-material");
    const modalPrecio = document.getElementById("modal-precio");
    const modalClose = document.getElementById("modal-close");

    document.querySelectorAll(".card").forEach(card => {
        card.addEventListener("click", () => {
            modalImg.src = card.dataset.imagen;
            modalNombre.textContent = card.dataset.nombre;
            modalMaterial.textContent = card.dataset.material;
            modalPrecio.textContent = "Q" + card.dataset.precio;

            modal.classList.add("show");
            document.body.classList.add("modal-open");
        });
    });

    modalClose.addEventListener("click", () => {
        modal.classList.remove("show");
        document.body.classList.remove("modal-open");
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("show");
            document.body.classList.remove("modal-open");
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modal.classList.contains("show")) {
            modal.classList.remove("show");
            document.body.classList.remove("modal-open");
        }
    });
});
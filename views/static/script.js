document.addEventListener("DOMContentLoaded", function () {
    let izbranaVrstica = null;

    document.querySelectorAll(".klikabilna-vrstica").forEach(function (row) {
        row.addEventListener("click", function () {
            // Počisti prejšnjo izbiro
            if (izbranaVrstica) {
                izbranaVrstica.classList.remove("izbrana");
            }

            // Označi novo izbrano vrstico
            this.classList.add("izbrana");
            izbranaVrstica = this;

            // Shrani ID izbrane dirke
            let dirkaId = this.getAttribute("data-id");
            document.getElementById("izbrana_dirka").value = dirkaId;

            // Omogoči gumb za potrditev
            document.getElementById("potrdiPrijavo").disabled = false;
        });
    });

    document.getElementById("potrdiPrijavo").addEventListener("click", function () {
        let dirkaId = document.getElementById("izbrana_dirka").value;
        if (dirkaId) {
            window.location.href = `/prijava_dirka?id_dirke=${dirkaId}`;
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const seznam = document.getElementById("tekmovalci");
    let dragging = null;

    seznam.addEventListener("dragstart", function (e) {
        if (e.target.classList.contains("drag-item")) {
            dragging = e.target;
            e.target.classList.add("dragging");
        }
    });

    seznam.addEventListener("dragend", function (e) {
        e.target.classList.remove("dragging");
        dragging = null;
    });

    seznam.addEventListener("dragover", function (e) {
        e.preventDefault();
        const afterElement = getDragAfterElement(seznam, e.clientY);
        if (afterElement == null) {
            seznam.appendChild(dragging);
        } else {
            seznam.insertBefore(dragging, afterElement);
        }
    });

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll(".drag-item:not(.dragging)")];
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    // 🔁 Ob oddaji forme ustvarimo hidden inpute v pravilnem vrstnem redu
    const form = document.getElementById("rezultat-form");
    form.addEventListener("submit", function (e) {
        const container = document.getElementById("skriti-vnosi");
        container.innerHTML = ""; // počisti staro

        const items = seznam.querySelectorAll(".drag-item");
        items.forEach((item) => {
            const hiddenInput = document.createElement("input");
            hiddenInput.type = "hidden";
            hiddenInput.name = "rezultat[]";
            hiddenInput.value = item.dataset.username;
            container.appendChild(hiddenInput);
        });
    });
});


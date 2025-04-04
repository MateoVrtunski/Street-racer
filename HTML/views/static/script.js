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
    if (seznam) {
        let dragging;

        seznam.addEventListener("dragstart", function (e) {
            if (e.target && e.target.classList.contains("drag-item")) {
                dragging = e.target;
                dragging.classList.add("dragging");
            }
        });

        seznam.addEventListener("dragend", function (e) {
            if (dragging) {
                dragging.classList.remove("dragging");
                dragging = null;
            }
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

        const form = document.querySelector("form");
        form.addEventListener("submit", function () {
            const items = seznam.querySelectorAll("li");
            items.forEach((li) => {
                const input = li.querySelector("input[name='rezultat[]']");
                input.value = li.textContent.trim();
            });
        });
    }
});


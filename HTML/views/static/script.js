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

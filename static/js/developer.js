window.onload = function() {
    console.log("Developer page loaded");
    var printButton = document.getElementById("print_test_button");
    var generatePdfButton = document.getElementById("generate_pdf_button");
    var result = document.getElementById("result");

    if (printButton) {
        printButton.addEventListener("click", function () {
            result.textContent = "Initiating print test...";
            fetch("/developer/print_test", {
                method: "POST",
            })
                .then((response) => {
                    if (!response.ok) {
                        return response.text().then((text) => {
                            result.textContent = text;
                        });
                    } else {
                        result.textContent = "Print test: ok";
                    }
                })
        });
    }

    if (generatePdfButton) {
        generatePdfButton.addEventListener("click", function () {
            result.textContent = "Initiating PDF generation test...";
            fetch("/developer/generate_pdf_test", {
                method: "POST",
            })
                .then((response) => {
                    if (!response.ok) {
                        return response.text().then((text) => {
                            result.textContent = text;
                        });
                    } else {
                        result.textContent = "PDF generation test: ok";
                    }
                })
        });
    }
};
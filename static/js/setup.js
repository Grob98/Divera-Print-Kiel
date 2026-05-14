window.onload = function() {
    console.log("Setup page loaded");
    var savePdfSettingsButton = document.getElementById("save_pdf_settings_button");

    if (savePdfSettingsButton) {
        let cntOperationInfoInput = document.getElementById("cnt_operation_info");
        let cntHydrantMapInput = document.getElementById("cnt_hydrant_map");
        let result = document.getElementById("save_result");

        savePdfSettingsButton.addEventListener("click", function () {
            fetch("/setup/pdf_settings", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    operation_info_copies: cntOperationInfoInput.value,
                    hydrant_map_copies: cntHydrantMapInput.value
                })
            })
                .then((response) => {
                    if (!response.ok) {
                        return response.text().then((text) => {
                            result.textContent = text;
                        });
                    } else {
                        result.textContent = "Gespeichert";
                    }
                })
        });
    }
};
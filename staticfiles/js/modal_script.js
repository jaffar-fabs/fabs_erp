document.addEventListener("DOMContentLoaded", function () {
    let editButtons = document.querySelectorAll(".edit-btn");
    let deleteButtons = document.querySelectorAll(".delete-btn");
    let confirmDeleteBtn = document.querySelector("#confirmDeleteBtn");
    let baseCodeInput = document.querySelector("#offcanvas_edit input[name='base_code']");
    let baseDescriptionInput = document.querySelector("#offcanvas_edit input[name='base_description']");
    let pipelineListing = document.querySelector(".pipeline-listing");
    let deleteBaseCode, deleteBaseValue;

    if (editButtons && baseCodeInput && baseDescriptionInput && pipelineListing) {
        editButtons.forEach(button => {
            button.addEventListener("click", function () {
                let baseCode = this.getAttribute("data-base_code");
                let baseDescription = this.getAttribute("data-base_description");
                baseCodeInput.value = baseCode;
                baseDescriptionInput.value = baseDescription.toUpperCase();
                fetchBaseValues(baseCode);
            })
        })

        function fetchBaseValues(baseCode) {
            let formData = new FormData();
            formData.append("base_code", baseCode);

            fetch("{% url 'code_master_list' %}", {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) { displayBaseValues(data.base_values, baseCode) }
                })
        }

        function displayBaseValues(baseValues, baseCode) {
            pipelineListing.innerHTML = "";
            if (baseValues.length === 0) {
                let noValuesMessage = document.createElement("div");
                noValuesMessage.className = "pipeline-item";
                noValuesMessage.textContent = "No base values found.";
                pipelineListing.appendChild(noValuesMessage);
            }
            else {
                baseValues.forEach(value => {
                    let item = document.createElement("div");
                    item.className = "pipeline-item";
                    let isActiveBadge = value.is_active === "Y" ? "bg-success" : "bg-danger";
                    let isActiveText = value.is_active === "Y" ? "Active" : "Inactive";
                    item.innerHTML = `
                        <p><i class="ti ti-grip-vertical"></i> ${value.base_value}</p>
                        <div class="action-pipeline">
                            <a>
                                <span class="badge badge-pill ${isActiveBadge}">
                                    ${isActiveText}
                                </span>
                            </a>
                            <a href="#" class="edit-base-value" data-base_code="${baseCode}" data-base_value="${value.base_value}" data-bs-toggle="modal" data-bs-target="#edit_stage">
                                <i class="ti ti-edit text-blue"></i>Edit
                            </a>
                            <a href="#" class="delete-base-value" data-base_code="${baseCode}" data-base_value="${value.base_value}" data-bs-toggle="modal" data-bs-target="#delete_stage">
                                <i class="ti ti-trash text-danger"></i>Delete
                            </a>
                        </div>
                    `;
                    pipelineListing.appendChild(item);
                })

                document.querySelectorAll(".edit-base-value").forEach(button => {
                    button.addEventListener("click", function () {
                        let baseCode = this.getAttribute("data-base_code");
                        let baseValue = this.getAttribute("data-base_value");
                        fetchBaseDescription(baseCode, baseValue);
                    })
                })

                document.querySelectorAll(".delete-base-value").forEach(button => {
                    button.addEventListener("click", function () {
                        deleteBaseCode = this.getAttribute("data-base_code");
                        deleteBaseValue = this.getAttribute("data-base_value");
                    })
                })
            }
        }

        function fetchBaseDescription(baseCode, baseValue) {
            let formData = new FormData();
            formData.append("base_code", baseCode);
            formData.append("base_value", baseValue);
            formData.append("request_type", "fetch_base_description");

            fetch("{% url 'code_master_list' %}", {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.querySelector("#editStageForm input[name='base_description']").value = data.base_description;
                        document.querySelector("#editStageForm input[name='base_value']").value = baseValue;
                        document.querySelector("#editStageForm input[name='base_type']").value = baseCode;
                        document.querySelector("#editStageForm input[name='is_active']").checked = data.is_active;
                    }
                });
        }

        document.querySelector("#editStageForm").addEventListener("submit", function (event) {
            event.preventDefault();

            let formData = new FormData(this);
            formData.append("request_type", "update_base_description");

            let isActive = document.querySelector("#editStageForm input[name='is_active']").checked ? "Y" : "N";
            formData.set("is_active", isActive);

            let baseCode = document.querySelector("#editStageForm input[name='base_type']").value;
            formData.set("base_code", baseCode);

            fetch("{% url 'code_master_list' %}", {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    }
                });
        });

        confirmDeleteBtn.addEventListener("click", function () {
            let formData = new FormData();
            formData.append("base_code", deleteBaseCode);
            formData.append("base_value", deleteBaseValue);
            formData.append("request_type", "delete_base_value");

            fetch("{% url 'code_master_list' %}", {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) { window.location.reload() }
                })
        })
    }

    // Remove the backdrop element when the modal is shown
    let modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function () {
            let backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        });
    });
});

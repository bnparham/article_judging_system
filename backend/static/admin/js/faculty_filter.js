document.addEventListener("DOMContentLoaded", function() {
    const facultyField = document.getElementById("id_faculty");
    const eduGroupField = document.getElementById("id_educational_group");

    function updateEducationalGroups() {
        const selectedFaculty = facultyField.value;
        eduGroupField.innerHTML = ""; // Clear previous options

        if (!selectedFaculty) return; // Exit if no faculty is selected

        // Call API to get educational groups
        fetch(`/uni/api/educational-groups/?faculty=${selectedFaculty}`)
            .then(response => response.json())
            .then(data => {
                if (data.educational_groups) {
                    data.educational_groups.forEach(([value, label]) => {
                        const option = document.createElement("option");
                        option.value = value;
                        option.textContent = label;
                        eduGroupField.appendChild(option);
                    });
                }
            })
            .catch(error => console.error("Error fetching educational groups:", error));
    }

    facultyField.addEventListener("change", updateEducationalGroups);
    updateEducationalGroups(); // Call it initially
});

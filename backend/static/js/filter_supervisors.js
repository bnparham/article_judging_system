(function() {
    // Wait for the document to load completely
    document.addEventListener('DOMContentLoaded', function() {
        const scheduleField = document.getElementById('id_schedule');  // Schedule field ID
        const supervisor1Field = document.getElementById('id_supervisor1');  // Supervisor1 field ID
        const supervisor2Field = document.getElementById('id_supervisor2');  // Supervisor2 field ID
        const supervisor3Field = document.getElementById('id_supervisor3');  // Supervisor3 field ID
        const supervisor4Field = document.getElementById('id_supervisor4');  // Supervisor4 field ID

        // Function to update supervisor options
        function updateSupervisorOptions() {
            const selectedSchedule = scheduleField.value;
            if (!selectedSchedule) return;  // Exit if no schedule is selected

            // Fetch the available supervisors dynamically based on the selected schedule
            fetch(`/assignment/admin/session/filter_supervisors/${selectedSchedule}/`)  // URL to fetch filtered supervisors
                .then(response => response.json())
                .then(data => {
                    // Clear current options
                    supervisor1Field.innerHTML = '';
                    supervisor2Field.innerHTML = '';
                    supervisor3Field.innerHTML = '';
                    supervisor4Field.innerHTML = '';


                    const nullOption = new Option('---------', '');  // Create a blank option
                    supervisor1Field.add(nullOption);
                    supervisor2Field.add(nullOption.cloneNode(true));
                    supervisor3Field.add(nullOption.cloneNode(true));
                    supervisor4Field.add(nullOption.cloneNode(true));

                    // Populate new supervisor options
                    data.supervisors.forEach(supervisor => {
                        const option = new Option(supervisor.name, supervisor.id);
                        supervisor1Field.add(option.cloneNode(true));
                        supervisor2Field.add(option.cloneNode(true));
                        supervisor3Field.add(option.cloneNode(true));
                        supervisor4Field.add(option.cloneNode(true));
                    });
                })
                .catch(error => console.error('Error fetching supervisor data:', error));
        }

        // Add event listener to update supervisors when schedule changes
        scheduleField.addEventListener('change', updateSupervisorOptions);
    });
})();

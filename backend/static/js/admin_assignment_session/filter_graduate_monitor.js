(function() {
    // Wait for the document to load completely
    document.addEventListener('DOMContentLoaded', function() {
        const scheduleField = document.getElementById('id_schedule');  // Schedule field ID
        const graduateMonitorField = document.getElementById('id_graduate_monitor');  // Supervisor1 field ID

        // Function to get session ID from the URL
        function getSessionIdFromUrl() {
            const urlPath = window.location.pathname; // Get the full URL path
            const sessionId = urlPath.split('/')[4]; // Assuming the session ID is the 5th segment of the URL
            return sessionId;
        }


        // Function to update supervisor options
        function updateSupervisorOptions() {
            const selectedSchedule = scheduleField.value;
            if (!selectedSchedule) return;  // Exit if no schedule is selected

            // Get session ID from the URL
            const sessionId = getSessionIdFromUrl();

            // Fetch the available supervisors dynamically based on the selected schedule
            fetch(`/assignment/admin/session/filter_graduate_monitor/${selectedSchedule}/${sessionId}/`)  // URL to fetch filtered supervisors
                .then(response => response.json())
                .then(data => {
                    // Clear current options
                    graduateMonitorField.innerHTML = '';

                    const nullOption = new Option('---------', '');  // Create a blank option
                    graduateMonitorField.add(nullOption);

                    // Populate new supervisor options
                    data.graduateMonitors.forEach(graduateMonitor => {
                        const option = new Option(graduateMonitor.name, graduateMonitor.id);
                        graduateMonitorField.add(option.cloneNode(true));
                    });
                })
                .catch(error => console.error('Error fetching supervisor data:', error));
        }

        // Add event listener to update supervisors when schedule changes
        scheduleField.addEventListener('change', updateSupervisorOptions);
    });
})();

(function() {
    // Wait for the document to load completely
    document.addEventListener('DOMContentLoaded', function() {
        const scheduleField = document.getElementById('id_schedule');  // Schedule field ID
        const judge1Field = document.getElementById('id_judge1');  // Judge1 field ID
        const judge2Field = document.getElementById('id_judge2');  // Judge2 field ID
        const judge3Field = document.getElementById('id_judge3');  // Judge3 field ID

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
            fetch(`/assignment/admin/session/filter_judges/${selectedSchedule}/${sessionId}/`)  // URL to fetch filtered supervisors
                .then(response => response.json())
                .then(data => {
                    // Clear current options
                    judge1Field.innerHTML = '';
                    judge2Field.innerHTML = '';
                    judge3Field.innerHTML = '';


                    const nullOption = new Option('---------', '');  // Create a blank option
                    judge1Field.add(nullOption);
                    judge2Field.add(nullOption.cloneNode(true));
                    judge3Field.add(nullOption.cloneNode(true));

                    // Populate new supervisor options
                    data.judges.forEach(judge => {
                        const option = new Option(judge.name, judge.id);
                        judge1Field.add(option.cloneNode(true));
                        judge2Field.add(option.cloneNode(true));
                        judge3Field.add(option.cloneNode(true));
                    });
                })
                .catch(error => console.error('Error fetching supervisor data:', error));
        }

        // Add event listener to update supervisors when schedule changes
        scheduleField.addEventListener('change', updateSupervisorOptions);
    });
})();

<!-- COMMAND TO RUN FRONTEND: `npm run dev` -->

<script>
	let message = "Loading...";

	fetch("http://localhost:8080/session-test", {
		credentials: "include"
	})
		.then(res => res.json())
		.then(data => {
			if ('session_id' in data && 'visit_count' in data) {
				message = `Session ID: ${data.session_id}, Visit count: ${data.visit_count}`;
			} else {
				message = "Unexpected response from backend!";
			}
		})
		.catch(error => {
			message = "Could not connect to backend!";
			console.error(error);
		});
</script>

<h1>{message}</h1>

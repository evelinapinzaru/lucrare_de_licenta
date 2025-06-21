<!-- COMMAND TO RUN FRONTEND: npm run dev -->

<script>
	let uploadedFile = null;
	let uploadMessage = "";

	async function handleUpload() {
		if (!uploadedFile) {
			uploadMessage = "Select a file to upload!";
			return;
		}

		const formData = new FormData();
		formData.append("file", uploadedFile);

		try {
			const res = await fetch("http://localhost:8080/upload", {
				method: "POST",
				body: formData
			});
			const data = await res.json();
			uploadMessage = `${data.message} (${data.filename})`;
		} catch (err) {
			uploadMessage = "File upload failed!";
			console.error(err);
		}
	}
</script>

<label for="file-input"><strong>Choose a file to upload:</strong></label><br /><br />
<input type="file" on:change={(e) => uploadedFile = e.target.files[0]} />
<button on:click={handleUpload}>Upload file</button>
<p>{uploadMessage}</p>
<!-- COMMAND TO RUN FRONTEND: npm run dev -->

<script>
	let uploadedFile = null;
	let uploadMessage = "";
    let concepts = [];
	let cooccurrenceMap = {};

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
			concepts = data.concepts || [];
			cooccurrenceMap = data.concept_links || {};
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

{#if concepts.length}
	<hr />
	<h2>Extracted concepts</h2>
	<ul>
		{#each concepts as concept}
			<li>
				<details>
					<summary>{concept}</summary>
					{#if cooccurrenceMap[concept] && Object.keys(cooccurrenceMap[concept]).length > 0}
						<ul>
							{#each Object.entries(cooccurrenceMap[concept]) as [linked, count]}
								<li>{linked} ({count})</li>
							{/each}
						</ul>
					{:else}
						<p>No linked concepts found.</p>
					{/if}
				</details>
			</li>
		{/each}
	</ul>
{/if}
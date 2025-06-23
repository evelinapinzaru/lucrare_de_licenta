<!-- COMMAND TO RUN FRONTEND: npm run dev -->

<script>
	let uploadedFile = null;
	let uploadMessage= "";
    let concepts = [];
	let conceptLinksMap = {};
	let masteredConcepts = {};
	let masteredCount = 0;

	async function handleUpload() {
		if (!uploadedFile) {
			uploadMessage= "Select a file to upload!";
			return;
		}

		const formData = new FormData();
		formData.append("file", uploadedFile);

		try {
			const res = await fetch("http://localhost:8080/upload", {
				method: "POST",
				body: formData,
				credentials: "include"
			});
			const data = await res.json();
			uploadMessage= `${data.message} (${data.filename})`;
			concepts = data.concepts || [];
			conceptLinksMap = data.concept_links || {};
			masteredCount = Object.values(masteredConcepts).filter(Boolean).length;
		} catch (err) {
			uploadMessage= "File upload failed!";
			console.error(err);
		}
	}

	async function markAsMastered(concept) {
		if (masteredConcepts[concept]) return;

		try {
			const res = await fetch("http://localhost:8080/mark", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				credentials: "include",
				body: JSON.stringify({ concept })
			});

			if (!res.ok) throw new Error("Failed to mark as mastered");
			masteredConcepts = { ...masteredConcepts, [concept]: true };
			masteredCount += 1;
		} catch (err) {
			console.error("Failed to mark as mastered", err);
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
	<p>{masteredCount} out of {concepts.length} concepts are already mastered.</p>
	<ul>
		{#each concepts as concept}
			<li>
				<strong>{concept}</strong>
				{#if masteredConcepts[concept]}
					<span style="color: green; margin-left: 10px;">(Mastered)</span>
				{:else}
					<button on:click={() => markAsMastered(concept)}>Mark as mastered</button>
				{/if}
			</li>
		{/each}
	</ul>

	<hr />
	<h2>Related Concepts</h2>
		{#each Object.entries(conceptLinksMap) as [concept, links]}
		<div>
			<h3>{concept}</h3>
			{#if Object.keys(links).length > 0}
				<ul>
					{#each Object.entries(links) as [linkedConcept, count]}
						<li>{linkedConcept} (seen together {count} times)</li>
					{/each}
				</ul>
			{:else}
				<p>No related concepts found.</p>
			{/if}
		</div>
	{/each}
{/if}
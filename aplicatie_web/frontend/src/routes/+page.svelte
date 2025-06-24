<!-- COMMAND TO RUN FRONTEND: npm run dev -->

<script>
	import { onMount } from 'svelte';
	let uploadedFile = null;
	let uploadMessage= "";
    let concepts = [];
	let conceptLinks = {};
	let masteredConcepts = {};
	let masteredCount = 0;
	let selectedConcept = '';
	let exerciseResult = null;
	let generatedExercise = '';
	let generatedHint = '';
	let userSolution = '';
	let feedback = '';

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
			conceptLinks = data.concept_links || {};
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

			if (!res.ok) throw new Error("Failed to mark concept as mastered!");
			masteredConcepts = { ...masteredConcepts, [concept]: true };
			masteredCount += 1;
		} catch (err) {
			console.error("Failed to mark concept as mastered!", err);
		}
	}

  async function generateExercise(concept) {
    selectedConcept = concept;
    const res = await fetch("http://localhost:8080/generate-exercise", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ concept })
    });

    const data = await res.json();
    const match = data.exercise?.match(/Exercise:\s*(.*?)\s*Hint:\s*(.*)/s);
    if (match) {
      generatedExercise = match[1].trim();
      generatedHint = match[2].trim();
    } else {
      generatedExercise = data.exercise || "The exercise couldn't be parsed!";
      generatedHint = '';
    }
    feedback = '';
    userSolution = '';
  }

  async function evaluateSolution() {
    const res = await fetch("http://localhost:8080/check-solution", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        concept: selectedConcept,
        exercise: generatedExercise,
        solution: userSolution
      })
    });

    const data = await res.json();
    feedback = data.feedback || 'Solution couldn\'t be evaluated!';
  }
</script>

<style>
  .concept { margin: 0.25rem 0; }
  .mastered { font-weight: bold; color: green; }
  .exercise-box { margin-top: 1rem; }
  textarea { width: 100%; height: 150px; }
  .feedback { margin-top: 1rem; }
</style>

<label for="file-input"><strong>Choose a file to upload:</strong></label><br /><br />
<input type="file" on:change={(e) => uploadedFile = e.target.files[0]} />
<button on:click={handleUpload}>Upload file</button>
<p>{uploadMessage}</p>

{#if concepts.length}
  <h2>Concepts ({masteredCount} / {concepts.length} mastered)</h2>
  <ul>
    {#each concepts as concept}
      <li class="concept">
        <span class:mastered={masteredConcepts[concept]}>
          {concept}
        </span>
        <button on:click={() => markAsMastered(concept)}>Mark as mastered</button>
        <button on:click={() => generateExercise(concept)}>Generate exercise</button>
      </li>
    {/each}
  </ul>
{/if}

{#if generatedExercise}
  <div class="exercise-box">
    <h3>Exercise for {selectedConcept}</h3>
    <pre>{generatedExercise}</pre>
    <p class="hint"><strong>Hint:</strong> {generatedHint}</p>

    <h4>Your Solution</h4>
    <textarea bind:value={userSolution}></textarea>
    <button on:click={evaluateSolution}>Submit Solution</button>

    {#if feedback}
      <div class="feedback">
        <h4>Feedback</h4>
        <p>{feedback}</p>
      </div>
    {/if}
  </div>
{/if}
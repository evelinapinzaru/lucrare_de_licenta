<!-- COMMAND TO RUN FRONTEND: npm run dev -->

<script>
    import '../global.css';
    import { Button } from 'flowbite-svelte';
    import { goto } from '$app/navigation';

	import { onMount } from 'svelte';
	let uploadedFile = null;
	let uploadMessage= "";
    let concepts = [];
	let conceptLinks = {};
	let masteredConcepts = {};
	let masteredCount = 0;
	let selectedConcept = '';
	let generatedExercise = '';
	let generatedHint = '';
	let userSolution = '';
	let feedback = '';
    let username = '';
    let password = '';
    let sessionUser  = '';
    let progress = { mastered: 0, unmastered: 0, total: 0 };

    function goToExercises() {
      goto('/exercises');
    }

    onMount(() => {
      username = '';
      password = '';
      uploadedFile = null;
      uploadMessage = '';
    });

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
            await fetchProgress();
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
            await fetchProgress();
		} catch (err) {
			console.error(err.message);
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

  async function register() {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);
    const res = await fetch("http://localhost:8080/register", {
      method: "POST",
      body: form
    });
    const data = await res.json();
    alert(data.message || data.error);
  }

  async function login() {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);
    const res = await fetch("http://localhost:8080/login", {
      method: "POST",
      credentials: "include",
      body: form
    });
    const data = await res.json();
    if (data.message) {
      sessionUser = username;
    } else {
      alert(data.error || "Login failed");
    }
  }

  async function logout() {
    await fetch("http://localhost:8080/logout", {
      method: "POST",
      credentials: "include"
    });
    sessionUser = '';
    uploadedFile = null;
    uploadMessage = '';
    concepts = [];
    conceptLinks = {};
    masteredConcepts = {};
    masteredCount = 0;
    selectedConcept = '';
    generatedExercise = '';
    generatedHint = '';
    userSolution = '';
    feedback = '';
    progress = { mastered: 0, unmastered: 0, total: 0 };
  }

  async function fetchProgress() {
    const res = await fetch("http://localhost:8080/progress", {
      credentials: "include"
    });
    progress = await res.json();
  }
</script>

<style>
  .concept { margin: 0.25rem 0; }
  .mastered { font-weight: bold; color: green; }
  .exercise-box { margin-top: 1rem; }
  textarea { width: 100%; height: 150px; }
  .feedback { margin-top: 1rem; }
</style>

<main class="flex justify-center items-center min-h-screen bg-gray-100">
  <div class="text-center">
    <h1 class="text-4xl font-bold mb-4">Welcome to CodeFlow</h1>
    <p class="text-xl mb-8">How would you like to learn programming today?</p>

    <Button on:click={goToExercises} class="mb-4 text-black bg-blue-500 hover:bg-blue-600">
      Coding Exercises
    </Button>
  </div>
</main>
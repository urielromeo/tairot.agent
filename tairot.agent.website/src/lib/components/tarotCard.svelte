<script>
	import { fly } from 'svelte/transition';
	import { onMount } from 'svelte';
	import { on } from 'svelte/events';
	let showContent = false;
	let scrollY = 0;

	function handleScroll() {
		scrollY = window.scrollY;
	}
	onMount(() => {
		showContent = true;
	});
</script>

<svelte:window on:scroll={handleScroll} />
{#if showContent}
	<div class="tarot-container" style="transform: translateY(calc(-13% - {scrollY}px));">
		<div class="tarot-card-wrapper">
			<div class="pop3d tarot-card" in:fly={{ y: 20, duration: 1000 }}>
				<img src="/images/cards/1.png" alt="Tarot Card 1" />
			</div>
			<div class="pop3d tarot-card" in:fly={{ y: 20, duration: 2000 }}>
				<img src="/images/cards/2.png" alt="Tarot Card 2" />
			</div>
			<div class="pop3d tarot-card" in:fly={{ y: 20, duration: 3000 }}>
				<img src="/images/cards/3.png" alt="Tarot Card 3" />
			</div>
			<div class="pop3d tarot-card" in:fly={{ y: 20, duration: 4000 }}>
				<img src="/images/cards/4.png" alt="Tarot Card 4" />
			</div>
			<div class="pop3d tarot-card" in:fly={{ y: 20, duration: 5000 }}>
				<img src="/images/cards/1.png" alt="Tarot Card 1" />
			</div>
			<div class="pop3d tarot-card" in:fly={{ y: 20, duration: 6000 }}>
				<img src="/images/cards/2.png" alt="Tarot Card 2" />
			</div>
			<div class="pop3d tarot-card" in:fly={{ y: 20, duration: 7000 }}>
				<img src="/images/cards/3.png" alt="Tarot Card 3" />
			</div>
			<div class="pop3d tarot-card" in:fly={{ y: 20, duration: 8000 }}>
				<img src="/images/cards/4.png" alt="Tarot Card 4" />
			</div>
		</div>
	</div>
{/if}

<style>
	.tarot-container {
		position: fixed;
		top: 50%;
		right: 0;
		transform: translateY(-50%);
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: -40px; /* Overlap the cards */
		z-index: 100;
	}

	.tarot-card-wrapper {
		/* Remove transform styles from the element that has the fly transition */
	}

	/* Apply the rotations to an inner element, or you can target .pop3d if needed */
	.pop3d {
		cursor: pointer;
		transform-style: preserve-3d;
		perspective: 1000px;
	}

	/* If you want to keep the rotation effects, wrap your image in an additional container */
	.tarot-card {
		width: min(33vw, 200px);
		position: relative;
		right: -50px; /* Start partially hidden */
		transition:
			transform 0.3s ease,
			right 0.3s ease;
	}

	/* Rotation styling for the card wrappers or a nested element */
	.tarot-card:nth-child(1) {
		transform: rotate(-15deg);
	}
	.tarot-card:nth-child(2) {
		transform: rotate(-7deg);
	}
	/* Add more rules as needed */

	.tarot-card:nth-child(3) {
		transform: rotate(7deg);
	}
	.tarot-card:nth-child(4) {
		transform: rotate(15deg);
	}
	.tarot-card:nth-child(5) {
		transform: rotate(-15deg);
	}
	.tarot-card:nth-child(6) {
		transform: rotate(-7deg);
	}
	.tarot-card:nth-child(7) {
		transform: rotate(7deg);
	}
	.tarot-card:nth-child(8) {
		transform: rotate(15deg);
	}

	/* Hover effect: slide out and straighten */
	.tarot-card:hover {
		right: 0;
		transform: rotate(0deg);
	}
	/* 3D hover effect */
	.pop3d {
		cursor: pointer;
		transform-style: preserve-3d;
		perspective: 1000px;
	}
</style>

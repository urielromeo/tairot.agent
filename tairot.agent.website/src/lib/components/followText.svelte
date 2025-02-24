<script>
	export let text = '';
	export let className = '';
	export let alwaysFollow = false;
	import { onMount, onDestroy } from 'svelte';
	let container;
	function documentonmousemove(event) {
		if (alwaysFollow) {
			onmousemove(event);
		}
	}
	// Mouse move handler to adjust rotation based on mouse position
	function onmousemove(event) {
		// check if container is :hover
		if (!container.matches(':hover') && !alwaysFollow) {
			return;
		}
		const target = container;
		const rect = target.getBoundingClientRect();
		const x = event.clientX - rect.left;
		const y = event.clientY - rect.top;
		const centerX = rect.width / 2;
		const centerY = rect.height / 2;

		// Calculate separate distance fractions from the center for both X and Y
		const dx = Math.abs(x - centerX) / centerX;
		const dy = Math.abs(y - centerY) / centerY;
		// Average those fractions into a single value
		const distFraction = (dx + dy) / 2;
		// Interpolate between 5 (center) and 2 (edges) using that distance fraction
		let cap = 5 - 3 * distFraction;

		// Calculate rotation using the new cap
		const rotateX = ((y - centerY) / centerY) * cap;
		const rotateY = ((x - centerX) / centerX) * cap;

		// Invert rotateX for a natural effect
		target.style.transform = `perspective(1000px) rotateX(${-rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
	}

	// Reset transformation on mouse leave
	function resetTransform(event) {
		if (alwaysFollow) return;
		event.currentTarget.style.transform =
			'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)';
	}
</script>

<svelte:document onmousemove={documentonmousemove} />
{#if text}
	<span bind:this={container} class="pop3d {className}" {onmousemove} {onmouseleave}>
		{text}
	</span>
{/if}

<style>
	.pop3d {
		display: inline-block;
		padding: 1rem;
		/* border: 1px solid #ccc; */
		cursor: pointer;
		transition: transform 0.2s ease-out;
		transform-style: preserve-3d;
		perspective: 1000px;
		text-align: center;
	}
</style>

<script>
	export let className = '';

	// Mouse move handler to adjust rotation based on mouse position
	function handleMouseMove(event) {
		const rect = event.currentTarget.getBoundingClientRect();
		const x = event.clientX - rect.left;
		const y = event.clientY - rect.top;
		const centerX = rect.width / 2;
		const centerY = rect.height / 2;

		// Calculate rotation (capped at 10 degrees)
		const rotateX = ((y - centerY) / centerY) * 10;
		const rotateY = ((x - centerX) / centerX) * 10;

		// Invert rotateX for a natural effect
		event.currentTarget.style.transform = `perspective(1000px) rotateX(${-rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
	}

	// Reset transformation on mouse leave
	function resetTransform(event) {
		event.currentTarget.style.transform =
			'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)';
	}
</script>

<div class="pop3d {className}" on:mousemove={handleMouseMove} on:mouseleave={resetTransform}>
	<slot />
</div>

<style>
	.pop3d {
		/* display: inline-block; */
		padding: 1rem;
		/* border: 1px solid #ccc; */
		cursor: pointer;
		transition: transform 0.2s ease-out;
		transform-style: preserve-3d;
		perspective: 1000px;
		text-align: center;
	}
</style>

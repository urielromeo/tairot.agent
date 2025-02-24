<script>
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

<a href="https://dorahacks.io/hackathon/sonic-defai-hackathon" target="_blank" class="pop3d">
	<div
		class="hackathon-footer atkinson-hyperlegible-800"
		on:mousemove={handleMouseMove}
		on:mouseleave={resetTransform}
	>
		👋 made with love for the <span>Sonic DeFAI Hackathon</span> ✨
	</div>
</a>

<style>
	/* stick the a to the bottom left of the view */
	a {
		position: sticky;
		bottom: 0;
		left: 0;
		margin-left: 1rem;
		margin-bottom: 1rem;
	}
	a:hover span {
		text-decoration: underline;
	}
	.pop3d {
		/* display: absolute; */
		/* position: absolute; */
		bottom: 0;
		left: 0;
		margin-left: 1rem;
		margin-bottom: 1rem;
		padding: 1rem;
		/* border: 1px solid #ccc; */
		cursor: pointer;
		transition: transform 0.2s ease-out;
		transform-style: preserve-3d;
		perspective: 1000px;
		text-align: center;
	}
	.hackathon-footer {
		margin-top: 2rem;
		border: 2px dashed #999;
		padding: 1rem;
		font-size: 1em;
		font-weight: bold;
		border-radius: 8px;
		text-align: center;
		border-color: rgba(29, 42, 81, 0.8);
		color: rgba(24, 52, 134, 0.8);
		position: absolute;
		left: 0;
		bottom: 0;
		margin-left: 1em;
		margin-bottom: 1em;
		cursor: pointer;
		min-width: 30vw;
	}
</style>

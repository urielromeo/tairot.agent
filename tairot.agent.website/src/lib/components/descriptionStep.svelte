<script>
	export let className = '';
	export let action = '';
	export let style = '';

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
	function onclick(event) {
		switch (action) {
			case 'open':
				window.open('https://dorahacks.io/hackathon/sonic-defai-hackathon', '_blank');
				break;
			case 'scroll':
				window.scrollTo(0, document.body.scrollHeight);
				break;
			case 'scroll-to-learn-more':
				document.getElementById('learn-more').scrollIntoView({ behavior: 'smooth' });
				break;
			default:
				break;
		}
	}
</script>

<div
	class="pop3d {className} how-it-works-div atkinson-hyperlegible-800"
	on:mousemove={handleMouseMove}
	on:mouseleave={resetTransform}
	on:click={onclick}
	{style}
>
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
		transition: all 0.2s ease;
		color: rgba(24, 52, 134, 0.8);
	}
	div.how-it-works-div {
		width: 50%;
		margin: 0 auto;
		padding: 1em;
		border-radius: 15px;
		text-align: center;
		margin-top: 1em;
		cursor: pointer;
		background: linear-gradient(135deg, rgba(0, 64, 255, 0.2), rgba(126, 17, 180, 0.11));
	}
</style>

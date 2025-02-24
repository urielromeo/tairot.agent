<script>
	import { onMount } from 'svelte';

	let container;
	let div1;
	let div2;
	let div3;
	let div4;
	let div5;
	let div6;
	let line;

	function updateConnector() {
		if (!container || !div1 || !div2 || !line) return;

		// Get container's position for relative calculations
		const containerRect = container.getBoundingClientRect();

		// Get the positions of div1 and div2
		const rect1 = div1.getBoundingClientRect();
		const rect2 = div2.getBoundingClientRect();

		// Calculate coordinates relative to the container
		const x1 = rect1.left - containerRect.left + rect1.width / 2;
		const y1 = rect1.top - containerRect.top + rect1.height;
		const x2 = rect2.left - containerRect.left + rect2.width / 2;
		const y2 = rect2.top - containerRect.top;

		// Update the line's coordinates
		line.setAttribute('x1', x1);
		line.setAttribute('y1', y1);
		line.setAttribute('x2', x2);
		line.setAttribute('y2', y2);
	}

	onMount(() => {
		updateConnector();
		window.addEventListener('resize', updateConnector);
		return () => {
			window.removeEventListener('resize', updateConnector);
		};
	});
</script>

<div bind:this={container} class="container">
	<div bind:this={div1} class="box atkinson-hyperlegible-400" style="top: 50px; left: 50px;">
		Defillama
	</div>
	<div bind:this={div2} class="box atkinson-hyperlegible-400" style="top: 150px; left: 50px;">
		Debridge
	</div>
	<div bind:this={div3} class="box atkinson-hyperlegible-400" style="top: 250px; left: 50px;">
		Allora
	</div>
	<div bind:this={div6} class="box atkinson-hyperlegible-400" style="top: 350px; left: 50px;">
		Sonic Chain
	</div>
	<div bind:this={div4} class="box atkinson-hyperlegible-400" style="top: 100px; left: 300px;">
		✨ tairot.agent 🔮
	</div>
	<div bind:this={div5} class="box atkinson-hyperlegible-400" style="top: 200px; left: 300px;">
		tairot.backend
	</div>
	<div bind:this={div7} class="box atkinson-hyperlegible-400" style="top: 300px; left: 300px;">
		tairot.bribe
	</div>
	<svg
		style="position: absolute; top: 0; left: 0; pointer-events: none; width: 100%; height: 100%;"
	>
		<defs>
			<!-- Define an arrow marker -->
			<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
				<polygon points="0 0, 10 3.5, 0 7" fill="black" />
			</marker>
		</defs>
		<line bind:this={line} stroke="black" stroke-width="2" stroke-dasharray="5,5" />
	</svg>
</div>

<style>
	.container {
		position: relative;
		width: 600px;
		height: 400px;
		/* border: 1px solid #ddd; */
		width: 80%;
	}

	.box {
		min-width: 150px;
		height: 50px;
		background: lightblue;
		/* border: 1px solid #ccc; */
		text-align: center;
		line-height: 50px;
		position: absolute;
		/* padding: 1em; */
		/* width: 50%; */
		border-radius: 15px;
		/* text-align: center; */
		/* margin-top: 1em; */
		cursor: pointer;
		background: linear-gradient(135deg, rgba(0, 64, 255, 0.2), rgba(126, 17, 180, 0.11));
	}
</style>

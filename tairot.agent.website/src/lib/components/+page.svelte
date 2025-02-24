<script>
	import FollowText from '$lib/components/followText.svelte';
	import Pop3d from '$lib/components/pop3d.svelte';
	import MadeWithLove from '$lib/components/madeWithLove.svelte';
	import TarotCard from '$lib/components/tarotCard.svelte';
</script>

<div class="centered page">
	<div class="flex flex-col items-center justify-center">
		<br />
		<br />
		<h1 class=" mb-4 text-6xl font-bold">
			<FollowText
				className="ghost-text atkinson-hyperlegible-700 pop3d"
				text="✨ tairot.agent 🪄"
				alwaysFollow={false}
			></FollowText>
		</h1>
		<Pop3d className="cta-div atkinson-hyperlegible-800">Try the telegram bot here 🤖</Pop3d>
	</div>
</div>
<div class="centered page">
	<p class="cool-text">Hello, world!</p>
</div>
<div class="centered page">
	<p>Hello, world!</p>
</div>
<div class="centered page">
	<p>Hello, world!</p>
</div>
<TarotCard></TarotCard>
<MadeWithLove></MadeWithLove>

<style>
	div.cta-div {
		border: 2px solid blue;
		padding: 1em;
		width: 50%;
		border-radius: 15px;
		text-align: center;
		margin-top: 1em;
		cursor: pointer;
	}
	div.cta-div:hover {
		background: linear-gradient(135deg, rgba(0, 64, 255, 0.8), rgba(126, 17, 180, 0.911));

		color: white;
	}
	.page {
		height: 100vh;
	}
	.card {
		width: 300px;
		padding: 20px;
		background: #fff;
		border-radius: 10px;
		text-align: center;
		box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
		transition:
			transform 0.2s ease,
			box-shadow 0.2s ease;
		/* This gives a perspective to the transformation */
		perspective: 1000px;
		cursor: pointer;
	}

	div.centered {
		height: 100%;
		width: 100%;
		background-color: #c5b99e;
		background-color: white;
	}

	.centered {
		display: flex;
		justify-content: center;
		align-items: center;
		flex-direction: column;
		height: 100%;
	}

	.glow {
		color: #1c1c1c;
		text-shadow: 0 0 15px #0037ff;
	}
</style>

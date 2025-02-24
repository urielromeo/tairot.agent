<script>
	import FollowText from '$lib/components/followText.svelte';
	import Pop3d from '$lib/components/pop3d.svelte';
	import MadeWithLove from '$lib/components/madeWithLove.svelte';
	import TarotCard from '$lib/components/tarotCard.svelte';
	import CallToAction from '$lib/components/callToAction.svelte';
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import DescriptionStep from '$lib/components/descriptionStep.svelte';
	import FollowTextTitle from '$lib/components/followTextTitle.svelte';
	let showContent = false;
	onMount(() => {
		// Delay showing content until after component mount
		showContent = true;
	});
</script>

{#if showContent}
	<div class="centered page" in:fly={{ y: 20, duration: 400 }}>
		<div class="flex flex-col items-center justify-center">
			<br />
			<br />
			<h1 class="mb-4 text-6xl font-bold">
				<FollowTextTitle className="ghost-text atkinson-hyperlegible-700 pop3d" alwaysFollow={false}
				></FollowTextTitle>
			</h1>
			<CallToAction action="open-telegram-bot">Try the telegram bot here 🤖</CallToAction>
			<CallToAction action="open-x-account">Follow tairot.agent on X 🐔</CallToAction>
			<CallToAction action="scroll-to-bribes">Bribe the agent 💰</CallToAction>
			<CallToAction action="scroll-to-learn-more">About this project 🔎</CallToAction>
			<CallToAction action="open-git-repo">Git Repo 💻</CallToAction>
		</div>
	</div>
	<div class="page ml-5" id="learn-more">
		<h1 class="ghost-text atkinson-hyperlegible-700 pop3d mb-5 text-center">
			What is this project?
		</h1>
		<p class="how-it-works-title mr-40 text-2xl">
			We created a multi-social agent that creates sonic chain market readings based on the state of
			the network. <br />
			It's built using
			<a class="underline" href="https://www.zerepy.org/" target="_blank">ZerePy</a>
			and it integrates
			<a class="underline" href="https://github.com/urielromeo/tairot.agent" target="_blank"
				>cool plugins</a
			>
			freshly baked by us 🍰 <br />
			We have a
			<a class="underline" href="https://github.com/urielromeo/tairot.agent" target="_blank"
				>telegram bot</a
			>
			and a <a class="underline" href="https://x.com/TAROT_LORD" target="_blank">twitter account</a>
			that you can follow to get the latest updates on the market.
		</p>
		<DescriptionStep style={``}>We begin by gathering info from the Sonic chain ⚡</DescriptionStep>
		<DescriptionStep>Then, the AI Agent waits patiently for telegram messages 📥</DescriptionStep>
		<DescriptionStep
			>When it is called for divination, it starts preparing the gathered data 🔮</DescriptionStep
		>
		<DescriptionStep>The Agent feels the market, and considers its <u>bribes</u> 💰</DescriptionStep
		>
		<DescriptionStep
			>When the reading is complete, it gets back to the user, with text and images 📜</DescriptionStep
		>
		<DescriptionStep
			>Additionally, the Agent posts twice a day on its <u>X account</u> 🐔</DescriptionStep
		>
	</div>
	<TarotCard></TarotCard>
	<MadeWithLove></MadeWithLove>
{/if}

<style>
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
	.how-it-works-title {
		background: linear-gradient(135deg, rgba(219, 194, 161, 0.28), rgba(150, 228, 166, 0.19));
		width: 50%;
		margin: 0 auto;
		padding: 1em;
		border-radius: 15px;
		box-shadow: 3px 4px 9px 1px rgba(170, 169, 169, 0.39);
	}
</style>

<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, slide } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { activeReport, loadSampleData } from '$lib/stores';
  import SummaryCards from '$lib/components/SummaryCards.svelte';
  import SuiteBreakdown from '$lib/components/SuiteBreakdown.svelte';
  import DurationHistogram from '$lib/components/DurationHistogram.svelte';
  import FailuresList from '$lib/components/FailuresList.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';

  onMount(() => {
    if (!$activeReport) {
      loadSampleData();
    }
  });

  $: hasData = !!$activeReport;
</script>

{#if hasData}
  <div class="space-y-6" transition:fade={{ duration: 300 }}>
    <!-- Summary Cards -->
    <SummaryCards report={$activeReport} />

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <SuiteBreakdown suites={$activeReport.suites} />
      <DurationHistogram tests={$activeReport.suites.flatMap(s => s.tests)} />
    </div>

    <!-- Failures List -->
    <FailuresList tests={$activeReport.suites.flatMap(s => s.tests)} />
  </div>
{:else}
  <EmptyState
    title="No Test Data"
    description="Upload a test report or load sample data to get started."
    actionLabel="Load Sample Data"
    onAction={loadSampleData}
  />
{/if}

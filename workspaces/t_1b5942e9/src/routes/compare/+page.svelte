<script lang="ts">
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { activeReport, comparisonReport, reports, comparisonReportId, loadSampleData } from '$lib/stores';
  import { compareReports } from '$lib/parsers';
  import EmptyState from '$lib/components/EmptyState.svelte';

  let comparison: ReturnType<typeof compareReports> | null = null;

  $: if ($activeReport && $comparisonReport) {
    comparison = compareReports($activeReport, $comparisonReport);
  }

  function selectComparisonReport(event: Event) {
    const target = event.target as HTMLSelectElement;
    comparisonReportId.set(target.value);
  }

  $: otherReports = reports;
</script>

{#if $activeReport && $comparisonReport && comparison}
  <div class="space-y-6" transition:fade>
    <!-- Report Selectors -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card">
        <label class="text-sm font-medium text-gray-500">Report A (Baseline)</label>
        <p class="text-lg font-semibold text-gray-900 mt-1">{$activeReport.name}</p>
        <p class="text-sm text-gray-500">{$activeReport.summary.total} tests, {$activeReport.summary.passRate.toFixed(1)}% pass rate</p>
      </div>
      <div class="card">
        <label class="text-sm font-medium text-gray-500">Report B (Comparison)</label>
        <select
          class="mt-1 w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
          value={$comparisonReportId || ''}
          on:change={selectComparisonReport}
        >
          {#each $otherReports as report}
            {#if report.id !== $activeReport.id}
              <option value={report.id}>{report.name}</option>
            {/if}
          {/each}
        </select>
        <p class="text-sm text-gray-500 mt-1">{$comparisonReport.summary.total} tests, {$comparisonReport.summary.passRate.toFixed(1)}% pass rate</p>
      </div>
    </div>

    <!-- Summary Diff -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card">
        <p class="text-sm text-gray-500">Pass Rate Change</p>
        <p class="text-2xl font-bold {$comparisonReport.summary.passRate >= $activeReport.summary.passRate ? 'text-green-600' : 'text-red-600'}">
          {$comparisonReport.summary.passRate >= $activeReport.summary.passRate ? '+' : ''}{($comparisonReport.summary.passRate - $activeReport.summary.passRate).toFixed(1)}%
        </p>
      </div>
      <div class="card">
        <p class="text-sm text-gray-500">Tests Added</p>
        <p class="text-2xl font-bold text-blue-600">{comparison.added.length}</p>
      </div>
      <div class="card">
        <p class="text-sm text-gray-500">Tests Removed</p>
        <p class="text-2xl font-bold text-orange-600">{comparison.removed.length}</p>
      </div>
      <div class="card">
        <p class="text-sm text-gray-500">Status Changed</p>
        <p class="text-2xl font-bold text-purple-600">{comparison.statusChanged.length}</p>
      </div>
    </div>

    <!-- Status Changes -->
    {#if comparison.statusChanged.length > 0}
      <div class="card">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Status Changes</h3>
        <div class="space-y-2 max-h-64 overflow-y-auto">
          {#each comparison.statusChanged as change}
            <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <span class="badge-fail">{change.from}</span>
              <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              <span class={change.to === 'passed' ? 'badge-pass' : 'badge-fail'}>{change.to}</span>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{change.test.name}</p>
                <p class="text-xs text-gray-500">{change.test.suite}</p>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Added Tests -->
    {#if comparison.added.length > 0}
      <div class="card">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">New Tests</h3>
        <div class="space-y-1 max-h-48 overflow-y-auto">
          {#each comparison.added as test}
            <div class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded">
              <span class="badge-pass">new</span>
              <span class="text-sm text-gray-900">{test.name}</span>
              <span class="text-xs text-gray-500 ml-auto">{test.suite}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Removed Tests -->
    {#if comparison.removed.length > 0}
      <div class="card">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Removed Tests</h3>
        <div class="space-y-1 max-h-48 overflow-y-auto">
          {#each comparison.removed as test}
            <div class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded">
              <span class="badge-fail">removed</span>
              <span class="text-sm text-gray-900 line-through">{test.name}</span>
              <span class="text-xs text-gray-500 ml-auto">{test.suite}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
{:else}
  <EmptyState
    title="Select Reports to Compare"
    description="Load at least two test reports to compare them side by side."
    actionLabel="Load Sample Data"
    onAction={loadSampleData}
  />
{/if}

<script lang="ts">
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { filteredTests, filters, availableSuites, activeReport, exportToJSON, exportToCSV, downloadFile } from '$lib/stores';
  import type { TestStatus, TestCase } from '$lib/types';

  let sortColumn: keyof TestCase = 'name';
  let sortDirection: 'asc' | 'desc' = 'asc';
  let currentPage = 1;
  const pageSize = 20;

  $: totalPages = Math.ceil($filteredTests.length / pageSize);
  $: sortedTests = [...$filteredTests].sort((a, b) => {
    let aVal: any = a[sortColumn];
    let bVal: any = b[sortColumn];
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = (bVal as string).toLowerCase();
    }
    if (sortDirection === 'asc') return aVal > bVal ? 1 : -1;
    return aVal < bVal ? 1 : -1;
  });
  $: paginatedTests = sortedTests.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  function toggleSort(column: keyof TestCase) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'asc';
    }
    currentPage = 1;
  }

  function toggleStatus(status: string) {
    const current = $filters.statuses;
    if (current.includes(status as TestStatus)) {
      filters.set({ ...$filters, statuses: current.filter((s) => s !== status) });
    } else {
      filters.set({ ...$filters, statuses: [...current, status as TestStatus] });
    }
    currentPage = 1;
  }

  function toggleSuite(suite: string) {
    const current = $filters.suites;
    if (current.includes(suite)) {
      filters.set({ ...$filters, suites: current.filter((s) => s !== suite) });
    } else {
      filters.set({ ...$filters, suites: [...current, suite] });
    }
    currentPage = 1;
  }

  function handleSearch(event: Event) {
    const query = (event.target as HTMLInputElement).value;
    filters.set({ ...$filters, searchQuery: query });
    currentPage = 1;
  }

  function exportJSON() {
    const content = exportToJSON($filteredTests);
    downloadFile(content, 'test-results.json', 'application/json');
  }

  function exportCSV() {
    const content = exportToCSV($filteredTests);
    downloadFile(content, 'test-results.csv', 'text/csv');
  }

  function prevPage() {
    if (currentPage > 1) currentPage--;
  }

  function nextPage() {
    if (currentPage < totalPages) currentPage++;
  }

  function statusBadgeClass(status: TestStatus): string {
    const map: Record<TestStatus, string> = {
      passed: 'badge-pass',
      failed: 'badge-fail',
      skipped: 'badge-skip',
      error: 'badge-error',
      pending: 'badge',
    };
    return map[status];
  }

  function handleSidebarClose() {
    // used by overlay
  }
</script>

<div class="space-y-4" transition:fade>
  <!-- Filters Bar -->
  <div class="card">
    <div class="flex flex-wrap gap-4 items-center">
      <!-- Search -->
      <div class="flex-1 min-w-[200px]">
        <input
          type="text"
          placeholder="Search test names..."
          value={$filters.searchQuery}
          on:input={handleSearch}
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <!-- Status Filters -->
      <div class="flex gap-2">
        {#each ['passed', 'failed', 'skipped', 'error'] as status}
          <button
            class="px-3 py-1.5 text-xs font-medium rounded-full border transition-colors"
            class:bg-green-100={status === 'passed' && $filters.statuses.includes(status)}
            class:border-green-300={status === 'passed' && $filters.statuses.includes(status)}
            class:text-green-700={status === 'passed' && $filters.statuses.includes(status)}
            class:bg-red-100={status === 'failed' && $filters.statuses.includes(status)}
            class:border-red-300={status === 'failed' && $filters.statuses.includes(status)}
            class:text-red-700={status === 'failed' && $filters.statuses.includes(status)}
            class:bg-yellow-100={status === 'skipped' && $filters.statuses.includes(status)}
            class:border-yellow-300={status === 'skipped' && $filters.statuses.includes(status)}
            class:text-yellow-700={status === 'skipped' && $filters.statuses.includes(status)}
            class:bg-purple-100={status === 'error' && $filters.statuses.includes(status)}
            class:border-purple-300={status === 'error' && $filters.statuses.includes(status)}
            class:text-purple-700={status === 'error' && $filters.statuses.includes(status)}
            class:bg-gray-50={!$filters.statuses.includes(status)}
            class:border-gray-200={!$filters.statuses.includes(status)}
            class:text-gray-600={!$filters.statuses.includes(status)}
            on:click={() => toggleStatus(status)}
          >
            {status}
          </button>
        {/each}
      </div>

      <!-- Export Buttons -->
      <div class="flex gap-2">
        <button class="btn-secondary text-sm" on:click={exportJSON}>Export JSON</button>
        <button class="btn-secondary text-sm" on:click={exportCSV}>Export CSV</button>
      </div>
    </div>

    <!-- Suite Filters -->
    {#if $availableSuites.length > 0}
      <div class="mt-3 pt-3 border-t border-gray-100">
        <span class="text-xs font-medium text-gray-500 mr-2">Suites:</span>
        <div class="flex flex-wrap gap-1 mt-1">
          {#each $availableSuites as suite}
            <button
              class="px-2 py-1 text-xs rounded border transition-colors"
              class:bg-blue-50={$filters.suites.includes(suite)}
              class:border-blue-200={$filters.suites.includes(suite)}
              class:text-blue-700={$filters.suites.includes(suite)}
              class:bg-white={!$filters.suites.includes(suite)}
              class:border-gray-200={!$filters.suites.includes(suite)}
              class:text-gray-600={!$filters.suites.includes(suite)}
              on:click={() => toggleSuite(suite)}
            >
              {suite}
            </button>
          {/each}
        </div>
      </div>
    {/if}
  </div>

  <!-- Results Count -->
  <div class="flex items-center justify-between">
    <p class="text-sm text-gray-500">
      Showing {paginatedTests.length} of {$filteredTests.length} tests
    </p>
  </div>

  <!-- Table -->
  <div class="card overflow-hidden p-0">
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-gray-600 cursor-pointer hover:bg-gray-100" on:click={() => toggleSort('name')}>
              Test Name {#if sortColumn === 'name'}{sortDirection === 'asc' ? '↑' : '↓'}{/if}
            </th>
            <th class="px-4 py-3 text-left font-medium text-gray-600 cursor-pointer hover:bg-gray-100" on:click={() => toggleSort('suite')}>
              Suite {#if sortColumn === 'suite'}{sortDirection === 'asc' ? '↑' : '↓'}{/if}
            </th>
            <th class="px-4 py-3 text-left font-medium text-gray-600 cursor-pointer hover:bg-gray-100" on:click={() => toggleSort('status')}>
              Status {#if sortColumn === 'status'}{sortDirection === 'asc' ? '↑' : '↓'}{/if}
            </th>
            <th class="px-4 py-3 text-left font-medium text-gray-600 cursor-pointer hover:bg-gray-100" on:click={() => toggleSort('duration')}>
              Duration {#if sortColumn === 'duration'}{sortDirection === 'asc' ? '↑' : '↓'}{/if}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          {#each paginatedTests as test (test.id)}
            <tr class="hover:bg-gray-50 transition-colors">
              <td class="px-4 py-3 font-medium text-gray-900">{test.name}</td>
              <td class="px-4 py-3 text-gray-600">{test.suite}</td>
              <td class="px-4 py-3">
                <span class={statusBadgeClass(test.status)}>{test.status}</span>
              </td>
              <td class="px-4 py-3 text-gray-600">{test.duration}ms</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    {#if totalPages > 1}
      <div class="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
        <button
          class="btn-secondary text-sm disabled:opacity-50"
          disabled={currentPage === 1}
          on:click={prevPage}
        >
          Previous
        </button>
        <span class="text-sm text-gray-600">
          Page {currentPage} of {totalPages}
        </span>
        <button
          class="btn-secondary text-sm disabled:opacity-50"
          disabled={currentPage === totalPages}
          on:click={nextPage}
        >
          Next
        </button>
      </div>
    {/if}
  </div>
</div>

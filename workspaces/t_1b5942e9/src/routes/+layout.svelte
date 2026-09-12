<script lang="ts">
  import { page } from '$app/stores';
  import { activeView, sidebarOpen, reports, activeReport, activeReportId } from '$lib/stores';
  import { goto } from '$app/navigation';

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', route: '/dashboard' },
    { id: 'tests', label: 'Test Cases', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4', route: '/tests' },
    { id: 'compare', label: 'Compare', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', route: '/compare' },
    { id: 'upload', label: 'Upload', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12', route: '/upload' },
  ];

  function navigate(view: string, route: string) {
    activeView.set(view as any);
    goto(route);
  }

  function onReportChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    activeReportId.set(target.value || null);
  }
</script>

<div class="flex h-screen bg-gray-50">
  <!-- Sidebar -->
  <aside
    class="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 lg:relative lg:translate-x-0"
    class:translate-x--full={!sidebarOpen}
  >
    <div class="flex flex-col h-full">
      <!-- Logo -->
      <div class="flex items-center gap-3 px-6 py-5 border-b border-gray-100">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <span class="font-bold text-lg text-gray-900">TestViz</span>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-3 py-4 space-y-1">
        {#each navItems as item}
          <button
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
            class:bg-blue-50={$activeView === item.id}
            class:text-blue-700={$activeView === item.id}
            class:text-gray-600={$activeView !== item.id}
            class:hover:bg-gray-50={$activeView !== item.id}
            on:click={() => navigate(item.id, item.route)}
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
            </svg>
            {item.label}
          </button>
        {/each}
      </nav>

      <!-- Report Selector -->
      {#if $reports.length > 0}
        <div class="px-3 pb-4 border-t border-gray-100 pt-4">
          <label for="report-select" class="text-xs font-medium text-gray-500 uppercase tracking-wider px-3">Active Report</label>
          <select
            id="report-select"
            class="mt-2 w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={$activeReportId || ''}
            on:change={onReportChange}
          >
            {#each $reports as report}
              <option value={report.id}>{report.name}</option>
            {/each}
          </select>
        </div>
      {/if}
    </div>
  </aside>

  <!-- Overlay for mobile -->
  {#if sidebarOpen}
    <div
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
      on:click={() => sidebarOpen.set(false)}
    />
  {/if}

  <!-- Main content -->
  <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
    <!-- Top bar -->
    <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div class="flex items-center gap-4">
        <button
          class="lg:hidden p-2 rounded-lg hover:bg-gray-100"
          on:click={() => sidebarOpen.set(!sidebarOpen)}
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 class="text-xl font-semibold text-gray-900">
          {#if $activeView === 'dashboard'}Dashboard{/if}
          {#if $activeView === 'tests'}Test Cases{/if}
          {#if $activeView === 'compare'}Compare Reports{/if}
          {#if $activeView === 'upload'}Upload Reports{/if}
        </h1>
      </div>

      <div class="flex items-center gap-3">
        {#if $activeReport}
          <span class="text-sm text-gray-500">
            {$activeReport.suites.length} suites, {$activeReport.summary.total} tests
          </span>
        {/if}
      </div>
    </header>

    <!-- Page content -->
    <main class="flex-1 overflow-auto p-6">
      <slot />
    </main>
  </div>
</div>

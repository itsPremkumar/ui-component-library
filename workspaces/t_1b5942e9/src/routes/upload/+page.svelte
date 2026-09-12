<script lang="ts">
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { isLoading, addReport, loadSampleData } from '$lib/stores';
  import { parseTestReport } from '$lib/parsers';
  import EmptyState from '$lib/components/EmptyState.svelte';

  let dragOver = false;
  let error: string | null = null;
  let successMessage: string | null = null;

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragOver = false;
    error = null;

    const files = e.dataTransfer?.files;
    if (files) {
      processFiles(Array.from(files));
    }
  }

  function handleFileInput(e: Event) {
    error = null;
    const input = e.target as HTMLInputElement;
    if (input.files) {
      processFiles(Array.from(input.files));
    }
  }

  async function processFiles(files: File[]) {
    isLoading.set(true);

    for (const file of files) {
      try {
        const content = await file.text();
        const report = parseTestReport(content);
        report.name = file.name;
        addReport(report);
        successMessage = `Loaded "${file.name}" successfully`;
      } catch (err) {
        error = `Failed to parse "${file.name}": ${err instanceof Error ? err.message : 'Unknown error'}`;
      }
    }

    isLoading.set(false);
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    dragOver = true;
  }

  function handleDragLeave() {
    dragOver = false;
  }
</script>

<div class="max-w-2xl mx-auto space-y-6" transition:fade>
  <!-- Drop Zone -->
  <div
    class="card border-2 border-dashed transition-all"
    class:border-blue-400={dragOver}
    class:bg-blue-50={dragOver}
    class:border-gray-200={!dragOver}
    role="button"
    tabindex="0"
    on:drop={handleDrop}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
  >
    <div class="flex flex-col items-center justify-center py-12 px-6 text-center">
      {#if $isLoading}
        <div class="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
        <p class="text-gray-600">Processing files...</p>
      {:else}
        <svg class="w-12 h-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-1">Drop test report files here</h3>
        <p class="text-sm text-gray-500 mb-4">Supports JUnit XML and JSON test reports</p>
        <label class="btn-primary cursor-pointer">
          Browse Files
          <input
            type="file"
            multiple
            accept=".xml,.json"
            class="hidden"
            on:change={handleFileInput}
          />
        </label>
      {/if}
    </div>
  </div>

  <!-- Messages -->
  {#if error}
    <div class="p-4 bg-red-50 border border-red-200 rounded-lg">
      <p class="text-sm text-red-700">{error}</p>
    </div>
  {/if}
  {#if successMessage}
    <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
      <p class="text-sm text-green-700">{successMessage}</p>
    </div>
  {/if}

  <!-- Demo Data -->
  <div class="card">
    <h3 class="text-lg font-medium text-gray-900 mb-2">Try with Sample Data</h3>
    <p class="text-sm text-gray-500 mb-4">Load generated test reports to explore the dashboard features.</p>
    <button class="btn-primary" on:click={loadSampleData}>Load Sample Reports</button>
  </div>

  <!-- Supported Formats -->
  <div class="card">
    <h3 class="text-lg font-medium text-gray-900 mb-3">Supported Formats</h3>
    <div class="space-y-3">
      <div class="flex items-start gap-3">
        <div class="w-8 h-8 bg-orange-100 rounded flex items-center justify-center flex-shrink-0">
          <span class="text-xs font-bold text-orange-600">XML</span>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">JUnit XML</p>
          <p class="text-xs text-gray-500">Standard JUnit format from most testing frameworks</p>
        </div>
      </div>
      <div class="flex items-start gap-3">
        <div class="w-8 h-8 bg-blue-100 rounded flex items-center justify-center flex-shrink-0">
          <span class="text-xs font-bold text-blue-600">JSON</span>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">JSON Reports</p>
          <p class="text-xs text-gray-500">Jest, Mocha, and custom JSON formats</p>
        </div>
      </div>
    </div>
  </div>
</div>

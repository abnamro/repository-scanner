<template>
  <div>
    <div class="row">
      <!-- Page size -->
      <div class="col-md-3 small">
        <small class="mr-1" v-if="itemPerPageDropdownEnabled">Items per page</small>
        <select
          v-if="itemPerPageDropdownEnabled"
          class="mt-1 custom-select-sm"
          v-model="selectedPageSize"
          @change="onPageSizeChange($event)"
        >
          <option v-for="size in pageSizes" :key="size" :value="size">
            {{ size }}
          </option>
        </select>
      </div>
      <div class="col-md-5 small">
        <!-- Pagination -->
        <b-pagination
          v-model="currentPageNumber"
          :per-page="props.perPage"
          :total-rows="props.totalRows"
          align="end"
          first-number
          last-number
          first-text="First"
          prev-text="Prev"
          next-text="Next"
          last-text="Last"
          pills
          @page-click="onPageClick"
        />
      </div>

      <!-- Total Record Count -->
      <div class="col-md-2 small">
        <ul class="pagination">
          <li class="page-item active">
            <a class="page-link">Total {{ props.totalRows }}</a>
          </li>
        </ul>
      </div>

      <!-- Go to page -->
      <div class="col-md-2 form-group mt-1 small" v-if="displayGoToPage">
        <label class="mr-1" for="go-to-page"><small>Go to page</small></label>
        <input
          type="number"
          class="go-to-page-input"
          name="go-to-page"
          v-model="goToPageNumber"
          min="1"
          :max="getTotalPageCount"
        />
        <input
          type="button"
          class="go-to-page-btn ml-1"
          value="Go"
          :disabled="goToPageButtonEnabled"
          v-on:click="handleGoToPage"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BvEvent } from 'bootstrap-vue-next';
import { computed, ref } from 'vue';
type Props = {
  currentPage: number;
  perPage: number;
  totalRows: number;
  pageSizes: number[];
  requestedPageNumber: number;
};
const props = defineProps<Props>();

const selectedPageSize = ref(props.perPage);
const currentPageNumber = ref(props.currentPage);
const goToPageNumber = ref(props.requestedPageNumber);

const getTotalPageCount = computed(() => {
  return Math.ceil(props.totalRows / props.perPage);
});
const displayGoToPage = computed(() => {
  return Math.ceil(props.totalRows / props.perPage) > 1;
});

const goToPageButtonEnabled = computed(() => {
  return goToPageNumber.value <= 0 || goToPageNumber.value > getTotalPageCount.value;
});
const itemPerPageDropdownEnabled = computed(() => {
  return props.totalRows >= props.perPage;
});

const emit = defineEmits(['page-size-change', 'page-click']);

function onPageClick(_event: BvEvent, page: number) {
  emit('page-click', page);
}

function onPageSizeChange(event: Event) {
  goToPageNumber.value = 1;
  // @ts-expect-error
  emit('page-size-change', event?.target?.value);
}

function handleGoToPage() {
  currentPageNumber.value = Number(goToPageNumber.value);
  emit('page-click', Number(goToPageNumber.value));
}
</script>

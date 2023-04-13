<template>
  <div>
    <div class="row">
      <!-- Page size -->
      <div class="col-md-3 small">
        <small class="mr-1">Items per page</small>
        <select
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
          :per-page="perPage"
          :total-rows="totalRows"
          align="right"
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
            <a class="page-link">Total {{ totalRows }}</a>
          </li>
        </ul>
      </div>

      <!-- Go to page -->
      <div class="col-md-2 form-group mt-1 small">
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
          :disabled="goToPageButtonDisabled"
          @click="handleGoToPage"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Pagination',
  props: {
    currentPage: {
      type: Number,
      required: true,
    },
    perPage: {
      type: Number,
      required: true,
    },
    totalRows: {
      type: Number,
      required: true,
    },
    pageSizes: {
      type: Array,
      required: true,
    },
    requestedPageNumber: {
      type: Number,
      required: true,
    },
  },
  computed: {
    getTotalPageCount() {
      return Math.ceil(this.totalRows / this.perPage);
    },
    goToPageButtonDisabled() {
      return this.goToPageNumber <= 0 || this.goToPageNumber > this.getTotalPageCount;
    },
  },
  data() {
    return {
      selectedPageSize: this.perPage,
      currentPageNumber: this.currentPage,
      goToPageNumber: this.requestedPageNumber,
    };
  },
  methods: {
    onPageClick(event, page) {
      this.$emit('page-click', page);
    },
    onPageSizeChange(event) {
      this.goToPageNumber = 1;
      this.$emit('page-size-change', event.target.value);
    },
    handleGoToPage() {
      this.currentPageNumber = Number(this.goToPageNumber);
      this.$emit('page-click', Number(this.goToPageNumber));
    },
  },
};
</script>

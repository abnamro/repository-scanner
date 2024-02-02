import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import App from '@/components/Common/PaginationVue.vue';
import { BPagination, BvEvent } from 'bootstrap-vue-next';

describe('Pagination data-line tests', () => {
  let wrapper;

  function initMountApp(options) {
    const { current_Page, per_Page, total_Rows, page_Sizes, requested_Page_Number } = options;
    wrapper = mount(App, {
      components: {
        BPagination: BPagination,
      },
      props: {
        currentPage: current_Page,
        perPage: per_Page,
        totalRows: total_Rows,
        pageSizes: page_Sizes,
        requestedPageNumber: requested_Page_Number,
      },
    });
  }

  it('Given a Pagination When props are passed then Pagination will be displayed', () => {
    initMountApp({
      current_Page: 2,
      per_Page: 20,
      total_Rows: 200,
      page_Sizes: [20, 50, 100],
      requested_Page_Number: 1,
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toContain('Items per page');
    expect(wrapper.html()).toContain('Prev');
    expect(wrapper.html()).toContain('Next');
    expect(wrapper.html()).toContain('Total 200');
    expect(wrapper.html()).toContain('Go to page');
    expect(() => wrapper.vm.onPageClick(new BvEvent('click'), 1)).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('page-click');
    expect(() => wrapper.vm.onPageSizeChange(50)).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('page-size-change');
  });

  it('Given a Pagination When props are passed then Pagination will be displayed', () => {
    initMountApp({
      current_Page: 1,
      per_Page: 20,
      total_Rows: 10,
      page_Sizes: [20, 50, 100],
      requested_Page_Number: 1,
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).not.toContain('Items per page');
    expect(wrapper.html()).toContain('Prev');
    expect(wrapper.html()).toContain('Next');
    expect(wrapper.html()).toContain('Total 10');
    expect(wrapper.html()).toContain('Go to page');
    expect(() => wrapper.vm.handleGoToPage()).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('page-click');
  });

  it('Given a Pagination When props are passed then Pagination will be displayed', () => {
    initMountApp({
      current_Page: 1,
      per_Page: 20,
      total_Rows: 10,
      page_Sizes: [20, 50, 100],
      requested_Page_Number: 1,
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).not.toContain('Items per page');
    expect(wrapper.html()).toContain('Prev');
    expect(wrapper.html()).toContain('Next');
    expect(wrapper.html()).toContain('Total 10');
    expect(wrapper.html()).toContain('Go to page');
  });
});

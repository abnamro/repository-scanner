import { mount } from '@vue/test-utils';
import App from '@/components/Common/Pagination';
import { BPagination } from 'bootstrap-vue';

describe('Pagination data-line tests', () => {
  let wrapper;

  const current_Page = 2;
  const per_Page = 20;
  const total_Rows = 10;
  const page_Sizes = [20, 50, 100];
  const requested_Page_Number = 1;

  function initMountApp(current_Page, per_Page, total_Rows, page_Sizes, requested_Page_Number) {
    wrapper = mount(App, {
      components: {
        BPagination: BPagination,
      },
      propsData: {
        currentPage: current_Page,
        perPage: per_Page,
        totalRows: total_Rows,
        pageSizes: page_Sizes,
        requestedPageNumber: requested_Page_Number,
      },
      data() {
        return {
          selectedPageSize: this.perPage,
          currentPageNumber: this.currentPage,
          goToPageNumber: this.requestedPageNumber,
        };
      },
    });
  }

  beforeEach(() => {
    initMountApp(current_Page, per_Page, total_Rows, page_Sizes, requested_Page_Number);
  });

  it('Given a Pagination When props are passed then Pagination will be displayed', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toContain('Items per page');
    expect(wrapper.html()).toContain('Prev');
    expect(wrapper.html()).toContain('Next');
    expect(wrapper.html()).toContain('Total 10');
    expect(wrapper.html()).toContain('Go to page');
  });
});

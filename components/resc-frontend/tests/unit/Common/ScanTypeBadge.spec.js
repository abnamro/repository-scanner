import { mount } from '@vue/test-utils';
import App from '@/components/Common/ScanTypeBadge';
import { BBadge } from 'bootstrap-vue';

describe('ScanTypeBadge data-line tests', () => {
  let wrapper;

  const scan_Type = 'BASE';
  const increment_Number = 2;

  function initMountApp(scan_Type, increment_Number) {
    wrapper = mount(App, {
      components: {
        BBadge: BBadge,
      },
      propsData: {
        scanType: scan_Type,
        incrementNumber: increment_Number,
      },
    });
  }

  beforeEach(() => {
    initMountApp(scan_Type, increment_Number);
  });

  it('Given a ScanTypeBadge When propsData is passed with scanType BASE then appropriate badge will be displayed', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toContain('BASE: 2');
  });

  it('Given a ScanTypeBadge When propsData is passed with scanType INCREMENTAL then appropriate badge will be displayed', () => {
    initMountApp('INCREMENTAL', increment_Number);
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toContain('INC: 2');
  });
});

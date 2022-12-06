import { mount } from '@vue/test-utils';
import App from '@/components/Common/Spinner';
import { BSpinner } from 'bootstrap-vue';

describe('Spinner data-line tests', () => {
  let wrapper;

  function initMountApp() {
    wrapper = mount(App, {
      components: {
        BSpinner: BSpinner,
      },
      propsData: {
        active: true,
      },
    });
  }

  beforeEach(() => {
    initMountApp();
  });

  it('Given a Spinner When active true is passed then Spinner will be displayed', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.findComponent(BSpinner).classes()).toContain('spinner');
  });
});

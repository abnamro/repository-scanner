import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import App from '@/components/Common/SpinnerVue.vue';
import { BSpinner } from 'bootstrap-vue-next';

describe('Spinner data-line tests', () => {
  it('Given a Spinner then Spinner will be displayed', () => {
    const wrapper = mount(App, {
      components: {
        BSpinner: BSpinner,
      },
    });
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.findComponent(BSpinner).classes()).toContain('spinner');
  });
});

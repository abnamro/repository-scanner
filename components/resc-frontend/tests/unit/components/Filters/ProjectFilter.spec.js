import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import App from '@/components/Filters/ProjectFilter.vue';
import { BFormGroup } from 'bootstrap-vue-next';
import Multiselect from 'vue-multiselect';

describe('ProjectFilter tests', () => {
  it('Given a ProjectFilter When props are passed then ProjectFilter will be displayed', () => {
    const wrapper = mount(App, {
      props: {
        projectOptions: ['project1', 'project2'],
      },
      components: {
        BFormGroup: BFormGroup,
        Multiselect: Multiselect,
      },
    });

    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.onProjectFilterChange()).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-project-change');
  });
});

import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import App from '@/components/Common/HealthBar.vue';
import { BPopover } from 'bootstrap-vue-next';

describe('HealthBar tests', () => {
  it('Given a HealthBar When props are passed then HealthBar will be displayed', () => {
    const wrapper = mount(App, {
      props: {
        truePositive: 5,
        falsePositive: 4,
        notAnalyzed: 3,
        underReview: 2,
        clarificationRequired: 1,
        totalCount: 15,
      },
      components: {
        BPopover: BPopover,
      },
    });

    expect(wrapper.exists()).toBe(true);
  });
});

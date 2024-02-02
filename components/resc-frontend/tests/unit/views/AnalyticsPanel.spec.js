import { shallowMount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import App from '@/views/AnalyticsPanel.vue';

describe('AnalyticsPanel tests', () => {
  let wrapper;

  function initMountApp() {
    wrapper = shallowMount(App);
  }

  it('Given a AnalyticsPanel then AnalyticsPanel will be displayed', () => {
    initMountApp();
    expect(wrapper.exists()).toBe(true);
  });
});

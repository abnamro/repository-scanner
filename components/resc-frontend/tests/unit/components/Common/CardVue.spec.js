import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/Common/CardVue.vue';
import { BTooltip } from 'bootstrap-vue-next';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { importFA } from '@/assets/font-awesome';

importFA();

describe('CardVue tests', () => {
  let spy;

  afterAll(() => {
    console.warn.mockRestore();
  });

  afterEach(() => {
    console.warn.mockClear();
  });

  beforeEach(() => {
    spy = vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  it('Given a Card When props are passed then Card will be displayed', async () => {
    const wrapper = mount(App, {
      props: {
        cardTitle: 'card-title',
        cardBodyContent: 'card-content',
        titleIcon: 'medal',
        titleIconColor: 'red',
        titleIconTooltip: 'this is a medal',
        contentColor: 'yellow',
        contentIcon: 'award',
        contentIconColor: 'green',
      },
      components: {
        BTooltip,
        FontAwesomeIcon,
      },
      global: {
        stubs: {},
      },
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.card-box').exists()).toBe(true);
    expect(wrapper.html()).toContain('card-title');
    expect(wrapper.html()).toContain('card-content');
    expect(spy).toHaveBeenCalled();
    expect(spy.mock.calls[0][0]).toContain('Target element not found');
  });

  it('Given a Card When minor props are passed then Card will be displayed', () => {
    const wrapper = mount(App, {
      props: {
        cardTitle: 'card-title',
      },
      global: {
        stubs: { FontAwesomeIcon: true },
      },
      components: {
        BTooltip: BTooltip,
      },
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.card-box').exists()).toBe(true);
    expect(wrapper.html()).toContain('card-title');
    expect(wrapper.vm.titleIconDefinition).toBe(null);
  });
});

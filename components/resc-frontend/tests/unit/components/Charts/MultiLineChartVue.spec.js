import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/Charts/MultiLineChartVue.vue';
import { Line } from 'vue-chartjs';

HTMLCanvasElement.prototype.getContext = vi.fn();

describe('MultilineChart tests', () => {
  let spy;
  afterAll(() => {
    console.error.mockRestore();
  });

  afterEach(() => {
    console.error.mockClear();
  });

  beforeEach(() => {
    spy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('Given a Chart When props are passed then Chart will be displayed', () => {
    const wrapper = mount(App, {
      props: {
        chartData: {
          labels: ['data1', 'data2'],
          datasets: [{ data: [1, 2, 3, 5] }, { data: [2, 2, 3, 4] }],
        },
      },
      components: {
        Line: Line,
      },
      global: {},
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('canvas').exists()).toBe(true);
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0]).toContain(
      "Failed to create chart: can't acquire context from the given item",
    );
  });

  it('Given a Chart When props are passed with style then Chart will be displayed', () => {
    const wrapper = mount(App, {
      props: {
        chartData: {
          labels: ['data1', 'data2'],
          datasets: [{ data: [0, 2, 3, 5] }, { data: [2, 2, 3, 4] }],
        },
        styles: { height: '300px', width: '200px' },
      },
      global: {},
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('canvas').exists()).toBe(true);
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0]).toContain(
      "Failed to create chart: can't acquire context from the given item",
    );
  });
});

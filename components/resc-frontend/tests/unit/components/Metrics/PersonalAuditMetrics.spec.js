import { shallowMount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/Metrics/PersonalAuditMetrics.vue';
import personal_audit from '@/../tests/resources/mock_personal_audits.json';
import personal_audit2 from '@/../tests/resources/mock_personal_audits2.json';
import personal_audit3 from '@/../tests/resources/mock_personal_audits3.json';
import personal_audit4 from '@/../tests/resources/mock_personal_audits4.json';
import personal_audit5 from '@/../tests/resources/mock_personal_audits5.json';
import personal_audit6 from '@/../tests/resources/mock_personal_audits6.json';
import MultiLineChartVue from '@/components/Charts/MultiLineChartVue.vue';
import CardVue from '@/components/Common/CardVue.vue';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';

vi.mock('axios');

describe('PersonalAuditMetrics tests', () => {
  function initMountApp() {
    const wrapper = shallowMount(App, {
      props: {},
      components: {
        SpinnerVue: SpinnerVue,
        MultiLineChartVue: MultiLineChartVue,
        CardVue: CardVue,
      },
    });

    return wrapper;
  }

  it('Given a PersonalAuditMetrics When rank 1 is passed then PersonalAuditMetrics will be displayed', () => {
    axios.get.mockResolvedValueOnce(personal_audit);
    const wrapper = initMountApp();
    expect(wrapper.exists()).toBe(true);
  });

  it('Given a PersonalAuditMetrics When rank 2 is passed then PersonalAuditMetrics will be displayed', () => {
    axios.get.mockResolvedValueOnce(personal_audit2);
    const wrapper = initMountApp();
    expect(wrapper.exists()).toBe(true);
  });

  it('Given a PersonalAuditMetrics When rank 3 is passed then PersonalAuditMetrics will be displayed', () => {
    axios.get.mockResolvedValueOnce(personal_audit3);
    const wrapper = initMountApp();
    expect(wrapper.exists()).toBe(true);
  });

  it('Given a PersonalAuditMetrics When rank 4 is passed then PersonalAuditMetrics will be displayed', () => {
    axios.get.mockResolvedValueOnce(personal_audit4);
    const wrapper = initMountApp();
    expect(wrapper.exists()).toBe(true);
  });

  it('Given a PersonalAuditMetrics When rank 11 is passed then PersonalAuditMetrics will be displayed', () => {
    axios.get.mockResolvedValueOnce(personal_audit5);
    const wrapper = initMountApp();
    expect(wrapper.exists()).toBe(true);
  });

  it('Given a PersonalAuditMetrics When rank 0 is passed then PersonalAuditMetrics will be displayed', () => {
    axios.get.mockResolvedValueOnce(personal_audit6);
    const wrapper = initMountApp();
    expect(wrapper.exists()).toBe(true);
  });
});

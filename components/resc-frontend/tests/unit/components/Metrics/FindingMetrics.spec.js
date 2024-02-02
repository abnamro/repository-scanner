import { shallowMount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/Metrics/FindingMetrics.vue';
import findings_status_counts_per_vcs_provider_per_week from '@/../tests/resources/mock_findings_status_count_by_vcs_provider_per_week.json';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';

vi.mock('axios');

describe('FindingMetrics tests', () => {
  it('Given a FindingMetrics When props are passed then FindingMetrics will be displayed', () => {
    axios.get.mockResolvedValueOnce({ data: findings_status_counts_per_vcs_provider_per_week });
    axios.get.mockResolvedValueOnce({ data: findings_status_counts_per_vcs_provider_per_week });
    axios.get.mockResolvedValueOnce({ data: findings_status_counts_per_vcs_provider_per_week });

    const wrapper = shallowMount(App, {
      props: {},
      components: {
        SpinnerVue,
      },
    });

    expect(wrapper.exists()).toBe(true);
  });
});

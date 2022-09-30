import { mount } from '@vue/test-utils';
import App from '@/components/Common/FindingStatusBadge';
import { BBadge } from 'bootstrap-vue';

describe('FindingStatusBadge data-line tests', () => {
  let wrapper;

  const status_notAnalyzed = 'NOT_ANALYZED';
  const status_underReveiw = 'UNDER_REVIEW';
  const status_clarificationRequired = 'CLARIFICATION_REQUIRED';
  const status_truePositive = 'TRUE_POSITIVE';
  const status_falsePositive = 'FALSE_POSITIVE';

  function initMountApp(status_type) {
    wrapper = mount(App, {
      components: {
        BBadge: BBadge,
      },
      propsData: {
        status: status_type,
      },
    });
  }

  beforeEach(() => {
    initMountApp(status_truePositive);
  });

  it('Given a FindingStatusBadge When status True positive is passed then True Positive badge will be displayed', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toContain('True Positive');
  });

  it('Given a FindingStatusBadge When status Not Analyzed is passed then Not Analyzed badge will be displayed', () => {
    initMountApp(status_notAnalyzed);
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toContain('Not Analyzed');
  });

  it('Given a FindingStatusBadge When status Under Review is passed then Under Review badge will be displayed', () => {
    initMountApp(status_underReveiw);
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toContain('Under Review');
  });

  it('Given a FindingStatusBadge When status Clarification Required is passed then Clarification Required badge will be displayed', () => {
    initMountApp(status_clarificationRequired);
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toContain('Clarification Required');
  });

  it('Given a FindingStatusBadge When status False Positive is passed then False Positive badge will be displayed', () => {
    initMountApp(status_falsePositive);
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.html()).toContain('False Positive');
  });
});

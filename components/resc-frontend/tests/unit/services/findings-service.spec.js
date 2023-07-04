import FindingsService from '@/services/findings-service';
import axios from 'axios';
import Config from '@/configuration/config';
import findings from '@/../tests/resources/mock_findings.json';
import detailed_findings from '@/../tests/resources/mock_detailed_findings.json';
import detailed_findings_with_rule_pack_version from '@/../tests/resources/mock_detailed_findings_with_rule_pack_version.json';
import finding_count_per_week from '@/../tests/resources/mock_findings_count_per_week.json';
import audits from '@/../tests/resources/mock_finding_audits.json';
import findings_status_counts_per_vcs_provider_per_week from '@/../tests/resources/mock_findings_status_count_by_vcs_provider_per_week.json';
import audit_count_by_auditor_per_week from '@/../tests/resources/mock_audit_count_by_auditor_per_week.json';

jest.mock('axios');

describe('function getFindingById', () => {
  it('fetch a single finding', async () => {
    // Mock axios response
    axios.get.mockResolvedValueOnce(findings.data[0]);

    const response = await FindingsService.getFindingById(0);

    expect(response).toBeDefined();
    expect(response).not.toBeNull();
    expect(response).toEqual(findings.data[0]);
  });
});

describe('function auditFindings', () => {
  it('update the status and comment of several findings (bulk update)', async () => {
    // Mock axios response
    axios.put.mockResolvedValueOnce(findings.data.slice(-2));

    const response = await FindingsService.auditFindings(
      [1, 2],
      `${Config.value('falsePositiveStatusVal')}`,
      'test'
    );
    expect(response).not.toBeDefined();
  });
});

describe('function getDetailedFindings', () => {
  describe('when API call is successful', () => {
    it('should return detailed findings list', async () => {
      axios.get.mockResolvedValueOnce(detailed_findings);
      const filterObj = {};
      filterObj.skip = 0;
      filterObj.limit = 100;
      filterObj.startDate = '2022-03-01T14:30:43';
      filterObj.endDate = '2022-03-20T14:30:43';
      filterObj.vcsProvider = `${Config.value('bitbucketVal')}`;
      filterObj.findingStatus = `${Config.value('notAnalyzedStatusVal')}`;
      filterObj.project = 'ABC';
      filterObj.repository = 'test';
      filterObj.branch = 'feature1';
      filterObj.rule = 'Hardcoded-Username';

      const response = await FindingsService.getDetailedFindings(filterObj);

      expect(response).toEqual(detailed_findings);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.data.length).toBe(1);
      expect(response.total).toBe(1);
      expect(response.limit).toBe(100);
      expect(response.skip).toBe(0);
    });
  });

  describe('function getDetailedFindings', () => {
    describe('when API call is successful', () => {
      it('should return detailed findings list', async () => {
        axios.get.mockResolvedValueOnce(detailed_findings_with_rule_pack_version);
        const filterObj = {};
        filterObj.skip = 0;
        filterObj.limit = 100;
        filterObj.startDate = '2022-03-01T14:30:43';
        filterObj.endDate = '2022-03-20T14:30:43';
        filterObj.vcsProvider = `${Config.value('bitbucketVal')}`;
        filterObj.findingStatus = `${Config.value('notAnalyzedStatusVal')}`;
        filterObj.project = 'ABC';
        filterObj.repository = 'test';
        filterObj.branch = 'feature1';
        filterObj.rule = 'Hardcoded-Username';
        filterObj.rulePackVersions = '0.0.0';

        const response = await FindingsService.getDetailedFindings(filterObj);

        expect(response).toEqual(detailed_findings_with_rule_pack_version);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.data.length).toBe(1);
        expect(response.total).toBe(1);
        expect(response.limit).toBe(100);
        expect(response.skip).toBe(0);
      });
    });

    describe('when API call fails', () => {
      it('getDetailedFindings should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await FindingsService.getDetailedFindings('not_valid')
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
            expect(response.data.length).toBe(0);
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });

  describe('function getFindingCountPerWeek', () => {
    describe('when getFindingCountPerWeek API call is successful', () => {
      it('should return finding count per week', async () => {
        axios.get.mockResolvedValueOnce(finding_count_per_week);

        const response = await FindingsService.getFindingCountPerWeek();

        expect(response).toEqual(finding_count_per_week);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.data[0].date_lable).toBe('2022-W01');
        expect(response.data[0].finding_count).toBe(15200);
      });
    });

    describe('when getFindingCountPerWeek API call fails', () => {
      it('getFindingCountPerWeek should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await FindingsService.getFindingCountPerWeek('not_valid')
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });

  describe('function getMetricsFindingsCountPerVcsProviderPerWeek', () => {
    describe('when getMetricsFindingsCountPerVcsProviderPerWeek API call is successful', () => {
      it('should return finding statuses count per vcs provider per week', async () => {
        axios.get.mockResolvedValueOnce(findings_status_counts_per_vcs_provider_per_week);

        const response = await FindingsService.getMetricsFindingsCountPerVcsProviderPerWeek();

        expect(response).toEqual(findings_status_counts_per_vcs_provider_per_week);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.length).toBe(13);
        expect(response[0].time_period).toBe('2023 W09');
        expect(response[0].total).toBe(0);
        expect(response[0].vcs_provider_finding_count.AZURE_DEVOPS).toBe(0);
      });
    });

    describe('when getMetricsFindingsCountPerVcsProviderPerWeek API call fails', () => {
      it('getMetricsFindingsCountPerVcsProviderPerWeek should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await FindingsService.getMetricsFindingsCountPerVcsProviderPerWeek('not_valid')
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });

  describe('function getUnTriagedCountPerVcsProviderPerWeek', () => {
    describe('when getUnTriagedCountPerVcsProviderPerWeek API call is successful', () => {
      it('should return finding statuses count per vcs provider per week', async () => {
        axios.get.mockResolvedValueOnce(findings_status_counts_per_vcs_provider_per_week);

        const response = await FindingsService.getUnTriagedCountPerVcsProviderPerWeek();

        expect(response).toEqual(findings_status_counts_per_vcs_provider_per_week);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.length).toBe(13);
        expect(response[0].time_period).toBe('2023 W09');
        expect(response[0].total).toBe(0);
        expect(response[0].vcs_provider_finding_count.AZURE_DEVOPS).toBe(0);
      });
    });

    describe('when getUnTriagedCountPerVcsProviderPerWeek API call fails', () => {
      it('getUnTriagedCountPerVcsProviderPerWeek should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await FindingsService.getUnTriagedCountPerVcsProviderPerWeek('not_valid')
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });

  describe('function getTruePositiveCountPerVcsProviderPerWeek', () => {
    describe('when getTruePositiveCountPerVcsProviderPerWeek API call is successful', () => {
      it('should return finding statuses count per vcs provider per week', async () => {
        axios.get.mockResolvedValueOnce(findings_status_counts_per_vcs_provider_per_week);

        const response = await FindingsService.getTruePositiveCountPerVcsProviderPerWeek();

        expect(response).toEqual(findings_status_counts_per_vcs_provider_per_week);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.length).toBe(13);
        expect(response[0].time_period).toBe('2023 W09');
        expect(response[0].total).toBe(0);
        expect(response[0].vcs_provider_finding_count.AZURE_DEVOPS).toBe(0);
      });
    });

    describe('when getTruePositiveCountPerVcsProviderPerWeek API call fails', () => {
      it('getTruePositiveCountPerVcsProviderPerWeek should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await FindingsService.getTruePositiveCountPerVcsProviderPerWeek('not_valid')
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });

  describe('function getFindingAudits', () => {
    describe('when getFindingAudits API call is successful', () => {
      it('should return finding count per week', async () => {
        axios.get.mockResolvedValueOnce(audits);

        const response = await FindingsService.getFindingAudits(1, 100, 0);

        expect(response).toEqual(audits);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.data.length).toBe(5);
        expect(response.total).toBe(5);
        expect(response.limit).toBe(100);
        expect(response.skip).toBe(0);
      });
    });

    describe('when getFindingAudits API call fails', () => {
      it('getFindingAudits should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await FindingsService.getFindingAudits('not_valid')
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });

    describe('function getAuditsByAuditorPerWeek', () => {
      describe('when getAuditsByAuditorPerWeek API call is successful', () => {
        it('should return audit counts per auditor per week', async () => {
          axios.get.mockResolvedValueOnce(audit_count_by_auditor_per_week);

          const response = await FindingsService.getAuditsByAuditorPerWeek();

          expect(response).toEqual(audit_count_by_auditor_per_week);
          expect(response).toBeDefined();
          expect(response).not.toBeNull();
          expect(response.length).toBe(13);
          expect(response[0].time_period).toBe('2023 W12');
          expect(response[0].total).toBe(0);
          expect(response[0].audit_by_auditor_count.Anonymous).toBe(0);
        });
      });

      describe('when getAuditsByAuditorPerWeek API call fails', () => {
        it('getAuditsByAuditorPerWeek should return error', async () => {
          axios.get.mockResolvedValueOnce([]);

          await FindingsService.getAuditsByAuditorPerWeek('not_valid')
            .then((response) => {
              expect(response).toEqual([]);
              expect(response).not.toBeNull();
            })
            .catch((error) => {
              expect(error).toBeDefined();
              expect(error).not.toBeNull();
            });
        });
      });
    });
  });
});

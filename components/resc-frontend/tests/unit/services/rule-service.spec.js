import axios from 'axios';
import RuleService from '@/services/rule-service';
import rules from '@/../tests/resources/mock_rules.json';
import rules_with_findings_status_count from '@/../tests/resources/mock_rules_with_findings_status_count.json';
import rule_packs from '@/../tests/resources/mock_rule_packs.json';

jest.mock('axios');

describe('function getRulePacks', () => {
  describe('when getRulePacks API call is successful', () => {
    it('should return all rule packs', async () => {
      axios.get.mockResolvedValueOnce(rule_packs);

      const response = await RuleService.getRulePacks(20, 0);

      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response).toEqual(rule_packs);
      expect(response.data.length).toBe(7);
      expect(response.data[0].version).toBe('0.0.0');
      expect(response.data[0].active).toBe(false);
      expect(response.data[0].global_allow_list).toBeNull();
      expect(response.data[1].version).toBe('0.0.1');
      expect(response.data[1].active).toBe(false);
      expect(response.data[1].global_allow_list).toBe(31);
      expect(response.total).toBe(7);
      expect(response.limit).toBe(100);
      expect(response.skip).toBe(0);
    });
  });

  describe('when getRulePacks API call fails', () => {
    it('getRulePacks should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await RuleService.getRulePacks('not_valid')
        .then((response) => {
          expect(response).toEqual([]);
          expect(response).not.toBeNull();
          expect(response.length).toBe(0);
        })
        .catch((error) => {
          expect(error).toBeDefined();
          expect(error).not.toBeNull();
        });
    });
  });
});

describe('function downloadRulePack', () => {
  describe('when downloadRulePack API call is successful', () => {
    it('should downlad the rulepack', async () => {
      const buffer = new ArrayBuffer();
      let rulePackVersion = '0.0.1';
      axios.get.mockResolvedValueOnce(buffer);

      const response = await RuleService.downloadRulePack(rulePackVersion);

      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response).toEqual(buffer);
    });
  });

  describe('when getRulePacks API call fails', () => {
    it('downloadRulePack should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await RuleService.downloadRulePack('not_valid')
        .then((response) => {
          expect(response).toEqual([]);
          expect(response).not.toBeNull();
          expect(response.length).toBe(0);
        })
        .catch((error) => {
          expect(error).toBeDefined();
          expect(error).not.toBeNull();
        });
    });
  });
});

describe('function getRulesWithFindingStatusCount', () => {
  describe('when getRulesWithFindingStatusCount API call is successful', () => {
    it('should return all distinct rules with their finding status count', async () => {
      axios.get.mockResolvedValueOnce(rules_with_findings_status_count);

      const response = await RuleService.getRulesWithFindingStatusCount();

      expect(response).toEqual(rules_with_findings_status_count);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(10);
      expect(response[0].rule_name).toBe('Rule-1');
      expect(response[0].finding_count).toBe(25);
      expect(response[0].finding_statuses_count[0].status).toBe('TRUE_POSITIVE');
      expect(response[0].finding_statuses_count[0].count).toBe(11);
      expect(response[0].finding_statuses_count[1].status).toBe('FALSE_POSITIVE');
      expect(response[0].finding_statuses_count[1].count).toBe(2);
      expect(response[0].finding_statuses_count[2].status).toBe('CLARIFICATION_REQUIRED');
      expect(response[0].finding_statuses_count[2].count).toBe(3);
      expect(response[0].finding_statuses_count[3].status).toBe('UNDER_REVIEW');
      expect(response[0].finding_statuses_count[3].count).toBe(4);
      expect(response[0].finding_statuses_count[4].status).toBe('NOT_ANALYZED');
      expect(response[0].finding_statuses_count[4].count).toBe(5);
    });
  });

  describe('when getRulesWithFindingStatusCount API call fails', () => {
    it('getRulesWithFindingStatusCount should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await RuleService.getRulesWithFindingStatusCount('not_valid')
        .then((response) => {
          expect(response).toEqual([]);
          expect(response).not.toBeNull();
          expect(response.length).toBe(0);
        })
        .catch((error) => {
          expect(error).toBeDefined();
          expect(error).not.toBeNull();
        });
    });
  });
});

describe('function getAllDetectedRules', () => {
  describe('when getAllDetectedRules API call is successful', () => {
    it('should return all distinct rules when no other filters are provided', async () => {
      axios.get.mockResolvedValueOnce(rules);

      const response = await RuleService.getAllDetectedRules(null, null, null, null, null, null);

      expect(response).toEqual(rules);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(9);
    });
  });

  describe('when getAllDetectedRules API call is successful', () => {
    it('should return all distinct rules when findings status filter provided', async () => {
      axios.get.mockResolvedValueOnce(rules);

      const response = await RuleService.getAllDetectedRules(
        ['NOT_ANALYZED', 'TRUE_POSITIVES'],
        null,
        null,
        null,
        null,
        null
      );

      expect(response).toEqual(rules);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(9);
    });
  });

  describe('when getAllDetectedRules API call is successful', () => {
    it('should return all distinct rules when vcs provider filter provided', async () => {
      axios.get.mockResolvedValueOnce(rules);

      const response = await RuleService.getAllDetectedRules(
        null,
        ['BITBUCKET', 'AZURE_DEVOPS'],
        null,
        null,
        null,
        null
      );

      expect(response).toEqual(rules);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(9);
    });
  });

  describe('when getAllDetectedRules API call is successful', () => {
    it('should return all distinct rules when project filter provided', async () => {
      axios.get.mockResolvedValueOnce(rules);

      const response = await RuleService.getAllDetectedRules(
        null,
        null,
        'project-A',
        null,
        null,
        null
      );

      expect(response).toEqual(rules);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(9);
    });
  });

  describe('when getAllDetectedRules API call is successful', () => {
    it('should return all distinct rules when repository filter provided', async () => {
      axios.get.mockResolvedValueOnce(rules);

      const response = await RuleService.getAllDetectedRules(
        null,
        null,
        null,
        'repository-A',
        null,
        null
      );

      expect(response).toEqual(rules);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(9);
    });
  });

  describe('when getAllDetectedRules API call is successful', () => {
    it('should return all distinct rules when start date filter provided', async () => {
      axios.get.mockResolvedValueOnce(rules);

      const response = await RuleService.getAllDetectedRules(
        null,
        null,
        null,
        null,
        '2022-05-01T00:00:00',
        null
      );

      expect(response).toEqual(rules);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(9);
    });
  });

  describe('when getAllDetectedRules API call is successful', () => {
    it('should return all distinct rules when end date filter provided', async () => {
      axios.get.mockResolvedValueOnce(rules);

      const response = await RuleService.getAllDetectedRules(
        null,
        null,
        null,
        null,
        null,
        '2022-06-01T23:59:59'
      );

      expect(response).toEqual(rules);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(9);
    });
  });

  describe('when getAllDetectedRules API call is successful', () => {
    it('should return all distinct rules when all filters provided', async () => {
      axios.get.mockResolvedValueOnce(rules);

      const response = await RuleService.getAllDetectedRules(
        ['NOT_ANALYZED', 'TRUE_POSITIVES'],
        ['BITBUCKET', 'AZURE_DEVOPS'],
        'project-A',
        'repository-A',
        '2022-05-01T00:00:00',
        '2022-06-01T23:59:59'
      );

      expect(response).toEqual(rules);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(9);
    });
  });

  describe('when getAllDetectedRules API call fails', () => {
    it('getAllDetectedRules should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await RuleService.getAllDetectedRules('not_valid')
        .then((response) => {
          expect(response).toEqual([]);
          expect(response).not.toBeNull();
          expect(response.length).toBe(0);
        })
        .catch((error) => {
          expect(error).toBeDefined();
          expect(error).not.toBeNull();
        });
    });
  });

  describe('function uploadRulePack', () => {
    describe('when uploadRulePack API call is successful', () => {
      it('should upload the rulepack', async () => {
        let ruleFile = new File([''], 'dummy_rule.TOML');
        axios.post.mockResolvedValueOnce({ status: 200 });

        const response = await RuleService.uploadRulePack(ruleFile);

        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.status).toEqual(200);
      });
    });

    describe('when uploadRulePack API call fails', () => {
      it('uploadRulePack should return error', async () => {
        axios.post.mockResolvedValueOnce({ status: 500 });

        await RuleService.uploadRulePack('not_valid')
          .then((response) => {
            expect(response).toBeDefined();
            expect(response).not.toBeNull();
            expect(response.status).toEqual(500);
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });
});

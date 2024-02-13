import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import Config from '@/configuration/config';
import RuleService from '@/services/rule-service';
import rules from '@/../tests/resources/mock_rules.json';
import rules_with_findings_status_count from '@/../tests/resources/mock_rules_with_findings_status_count.json';

vi.mock('axios');

describe('function getRulesWithFindingStatusCount', () => {
  describe('when getRulesWithFindingStatusCount API call is successful with valid rule pack versions filter', () => {
    it('should return all distinct rules with their finding status count', async () => {
      let rulePackVersions = ['1.0.0', '1.0.1'];
      axios.get.mockResolvedValueOnce(rules_with_findings_status_count);

      const response = await RuleService.getRulesWithFindingStatusCount(rulePackVersions);

      expect(response).toEqual(rules_with_findings_status_count);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(10);
      expect(response[0].rule_name).toBe('Rule-1');
      expect(response[0].finding_count).toBe(25);
      expect(response[0].finding_statuses_count[0].status).toBe(
        `${Config.value('truePostiveStatusVal')}`,
      );
      expect(response[0].finding_statuses_count[0].count).toBe(11);
      expect(response[0].finding_statuses_count[1].status).toBe(
        `${Config.value('falsePositiveStatusVal')}`,
      );
      expect(response[0].finding_statuses_count[1].count).toBe(2);
      expect(response[0].finding_statuses_count[2].status).toBe(
        `${Config.value('clarificationRequiredStatusVal')}`,
      );
      expect(response[0].finding_statuses_count[2].count).toBe(3);
      expect(response[0].finding_statuses_count[3].status).toBe(
        `${Config.value('underReviewStatusVal')}`,
      );
      expect(response[0].finding_statuses_count[3].count).toBe(4);
      expect(response[0].finding_statuses_count[4].status).toBe(
        `${Config.value('notAnalyzedStatusVal')}`,
      );
      expect(response[0].finding_statuses_count[4].count).toBe(5);
    });
  });

  describe('when getRulesWithFindingStatusCount API call fails with invalid rule pack versions filter', () => {
    it('getRulesWithFindingStatusCount should return error', async () => {
      let rulePackVersions = ['not_valid'];
      axios.get.mockResolvedValueOnce([]);

      await RuleService.getRulesWithFindingStatusCount(rulePackVersions)
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
        [`${Config.value('notAnalyzedStatusVal')}`, `${Config.value('truePostiveStatusVal')}`],
        null,
        null,
        null,
        null,
        null,
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
        [`${Config.value('bitbucketVal')}`, `${Config.value('azureDevOpsVal')}`],
        null,
        null,
        null,
        null,
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
        null,
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
        null,
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
        null,
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
        '2022-06-01T23:59:59',
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
        [`${Config.value('notAnalyzedStatusVal')}`, `${Config.value('truePostiveStatusVal')}`],
        [`${Config.value('bitbucketVal')}`, `${Config.value('azureDevOpsVal')}`],
        'project-A',
        'repository-A',
        '2022-05-01T00:00:00',
        '2022-06-01T23:59:59',
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
});

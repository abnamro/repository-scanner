import axios from 'axios';
import RulePackService from '@/services/rule-pack-service';
import rule_packs from '@/../tests/resources/mock_rule_packs.json';
import rule_tags from '@/../tests/resources/mock_rule_tags.json';

jest.mock('axios');

describe('function getRulePackVersions', () => {
  describe('when getRulePackVersions API call is successful', () => {
    it('should return all rule packs', async () => {
      axios.get.mockResolvedValueOnce(rule_packs);

      const response = await RulePackService.getRulePackVersions(20, 0);

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

  describe('when getRulePackVersions API call fails', () => {
    it('getRulePackVersions should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await RulePackService.getRulePackVersions('not_valid')
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

      const response = await RulePackService.downloadRulePack(rulePackVersion);

      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response).toEqual(buffer);
    });
  });

  describe('when getRulePacks API call fails', () => {
    it('downloadRulePack should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await RulePackService.downloadRulePack('not_valid')
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

describe('function uploadRulePack', () => {
  describe('when uploadRulePack API call is successful', () => {
    it('should upload the rulepack', async () => {
      let ruleFile = new File([''], 'dummy_rule.TOML');
      let version = '0.0.1';
      axios.post.mockResolvedValueOnce({ status: 200 });

      const response = await RulePackService.uploadRulePack(version, ruleFile);

      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.status).toEqual(200);
    });
  });

  describe('when uploadRulePack API call fails', () => {
    it('uploadRulePack should return error', async () => {
      axios.post.mockResolvedValueOnce({ status: 500 });

      await RulePackService.uploadRulePack('not_valid')
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

describe('function getRuleTagsByRulePackVersions', () => {
  describe('when getRuleTagsByRulePackVersions API call is successful', () => {
    it('should return all tags for provided rule pack versions', async () => {
      axios.get.mockResolvedValueOnce(rule_tags);
      const rulePackVersions = ['1.0.0', '1.0.1'];
      const response = await RulePackService.getRuleTagsByRulePackVersions(rulePackVersions);

      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response).toEqual(rule_tags);
      expect(response.data.length).toBe(4);
      expect(response.data[0]).toBe('Cli');
      expect(response.data[1]).toBe('Info');
      expect(response.data[2]).toBe('Warn');
      expect(response.data[3]).toBe('Sentinel');
    });
  });

  describe('when getRuleTagsByRulePackVersions API call fails', () => {
    it('getRuleTagsByRulePackVersions should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await RulePackService.getRuleTagsByRulePackVersions('not_valid')
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

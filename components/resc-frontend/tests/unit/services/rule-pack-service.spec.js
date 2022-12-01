import axios from 'axios';
import RulePackService from '@/services/rule-pack-service';
import rule_packs from '@/../tests/resources/mock_rule_packs.json';

jest.mock('axios');

describe('function getRulePacks', () => {
  describe('when getRulePacks API call is successful', () => {
    it('should return all rule packs', async () => {
      axios.get.mockResolvedValueOnce(rule_packs);

      const response = await RulePackService.getRulePacks(20, 0);

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

      await RulePackService.getRulePacks('not_valid')
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
      axios.post.mockResolvedValueOnce({ status: 200 });

      const response = await RulePackService.uploadRulePack(ruleFile);

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

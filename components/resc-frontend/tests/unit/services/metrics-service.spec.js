import axios from 'axios';
import MetricsService from '@/services/metrics-service';
import personal_audits from '@/../tests/resources/mock_personal_audits.json';

jest.mock('axios');

describe('function getPersonalAuditMetrics', () => {
  describe('when getPersonalAuditMetrics API call is successful', () => {
    it('should return personal audit metrics', async () => {
      axios.get.mockResolvedValueOnce(personal_audits);

      const response = await MetricsService.getPersonalAuditMetrics();

      expect(response).toEqual(personal_audits);
      expect(response.data).toBeDefined();
      expect(response.data).not.toBeNull();
      expect(response.data.today).toBe(10);
      expect(response.data.current_week).toBe(1);
      expect(response.data.last_week).toBe(8);
      expect(response.data.current_month).toBe(1);
      expect(response.data.current_year).toBe(16);
      expect(response.data.forever).toBe(16);
      expect(response.data.rank_current_week).toBe(1);
    });
  });

  describe('when getPersonalAuditMetrics API call fails', () => {
    it('getPersonalAuditMetrics should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await MetricsService.getPersonalAuditMetrics()
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

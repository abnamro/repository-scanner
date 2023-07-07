import DateUtils from '@/utils/date-utils';

describe('function sortListByDate', () => {
  it('sort list by date', async () => {
    const scanDateList = [
      { scanId: 1, scanDate: 'May 25, 2022, 02:46 PM', scanType: 'Base' },
      { scanId: 2, scanDate: 'May 21, 2022, 02:46 PM', scanType: 'Base' },
      { scanId: 3, scanDate: 'May 22, 2022, 02:46 PM', scanType: 'Base' },
    ];

    const expectedSortedScanDateList = [
      { scanId: 1, scanDate: 'May 25, 2022, 02:46 PM', scanType: 'Base' },
      { scanId: 3, scanDate: 'May 22, 2022, 02:46 PM', scanType: 'Base' },
      { scanId: 2, scanDate: 'May 21, 2022, 02:46 PM', scanType: 'Base' },
    ];

    const sortedDateList = scanDateList.sort(DateUtils.sortListByDate);
    expect(sortedDateList).toBeDefined();
    expect(sortedDateList).toHaveLength(3);
    expect(sortedDateList).toStrictEqual(expectedSortedScanDateList);
  });
});

describe('function formatDate', () => {
  it('format timestamp to human readable date with time', async () => {
    const formattedDate = DateUtils.formatDate('2022-05-19T14:47:28.587000');
    expect(formattedDate).toBeDefined();
    expect(formattedDate).toBe('May 19, 2022, 02:47 PM');
  });
});

describe('function getCurrentMonth', () => {
  it('getCurrentMonth', async () => {
    const currentMonth = DateUtils.getCurrentMonth();
    expect(currentMonth).toBeDefined();
    expect(currentMonth).toBe(new Date().toLocaleString('default', { month: 'long' }));
  });
});

describe('function getCurrentYear', () => {
  it('getCurrentYear', async () => {
    const currentYear = DateUtils.getCurrentYear();
    expect(currentYear).toBeDefined();
    expect(currentYear).toBe(new Date().getFullYear());
  });
});

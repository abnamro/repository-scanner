const DateUtils = {
  sortListByDate(a, b) {
    const date1 = new Date(a.scanDate);
    const date2 = new Date(b.scanDate);
    return date2 - date1;
  },

  formatDate(timestamp) {
    return new Date(timestamp).toLocaleDateString(['en-US'], {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  },

  getCurrentMonth() {
    const currentMonth = new Intl.DateTimeFormat('en-US', { month: 'long' }).format(new Date());
    return currentMonth;
  },

  getCurrentYear() {
    const date = new Date();
    const currentYear = date.getFullYear();
    return currentYear;
  },
};

export default DateUtils;

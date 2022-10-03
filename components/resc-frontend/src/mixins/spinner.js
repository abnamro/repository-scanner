export default {
  data: () => {
    return {
      spinnerActive: false,
    };
  },
  methods: {
    showSpinner() {
      this.spinnerActive = true;
    },
    hideSpinner() {
      this.spinnerActive = false;
    },
  },
};

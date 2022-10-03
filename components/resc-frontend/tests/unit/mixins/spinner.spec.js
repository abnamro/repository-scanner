import spinner from '@/mixins/spinner';

describe('Spinner unit test', () => {
  it('Given spinner when by default is initialized then spinnerActive is false', async () => {
    const spinner_active = false;
    expect(spinner.data().spinnerActive).toBe(spinner_active);
  });

  it('Given spinner active as true then showSpinner is called', async () => {
    const spinner_active = true;
    spinner.methods.showSpinner();
    expect(spinner.methods.spinnerActive).toBe(spinner_active);
  });

  it('Given spinner active as false then hideSpinner is called', async () => {
    const spinner_active = false;
    spinner.methods.hideSpinner();
    expect(spinner.methods.spinnerActive).toBe(spinner_active);
  });
});

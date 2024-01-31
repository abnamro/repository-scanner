import { toRaw } from './common-utils';

/**
 * Utilities to merge into a string query.
 */
const QueryUtils = {
  appendArrayIf(queryArg: string, arg: number[] | string[] | undefined | null): string {
    if (arg === undefined || arg === null || arg.length === 0 || arg.length === undefined) {
      return '';
    }

    return `&${queryArg}=${encodeURIComponent(JSON.stringify(toRaw(arg)))}`;
  },

  appendExplodArrayIf(queryArg: string, arg: number[] | string[] | undefined | null): string {
    if (arg === undefined || arg === null || arg.length === 0 || arg.length === undefined) {
      return '';
    }
    let params = '';
    arg.forEach((value) => {
      params += `&${queryArg}=${toRaw(value)}`;
    });
    return params;
  },

  appendIf(queryArg: string, arg: number | string | undefined | null, suffix: string = ''): string {
    if (arg === undefined || arg === '' || arg === null) {
      return '';
    }

    return `&${queryArg}=${toRaw(arg)}${suffix}`;
  },

  appendBool(queryArg: string, arg: boolean): string {
    if (arg) {
      return `&${queryArg}=true`;
    }

    return '';
  },
};

export default QueryUtils;

import child_process from 'child_process';

export function run(command: string) {
  try {
    child_process.exec(command);
  } catch (e) {
    console.error(`Unable to run command '${command}' due to error ${e}`);
  }
}

export function runSync(command: string) {
  try {
    child_process.execSync(command);
  } catch (e) {
    console.error(`Unable to run command '${command}' due to error ${e}`);
  }
}

export function redact(str: string | undefined): string | undefined {
  if (str === undefined) {
    return undefined;
  }

  const strlen = str.length;
  if (strlen <= 8) {
    return `[redacted ${strlen} chars]`;
  }

  return `${str.slice(0, 4)}[redacted ${strlen - 8} chars]${str.slice(-4)}`;
}

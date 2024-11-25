interface PasswordInfo {
  hasEightChars: boolean;
  hasSpecialChar: boolean;
  hasLetter: boolean;
  hasDigit: boolean;
}

export function getPasswordInfo(password: string): PasswordInfo {
  const specialCharRegExp = /[^a-zA-Z0-9]/g;
  const letterRegExp = /[a-zA-Z]/g;
  const digitRegExp = /[0-9]/g;
  return {
    hasEightChars: password.length >= 8,
    hasSpecialChar: specialCharRegExp.test(password),
    hasLetter: letterRegExp.test(password),
    hasDigit: digitRegExp.test(password),
  };
}

export function passwordIsValid({ hasEightChars, hasSpecialChar, hasLetter, hasDigit }: PasswordInfo): boolean {
  return hasEightChars && hasSpecialChar && hasLetter && hasDigit;
}

import type { KeyboardEvent } from "react";

const ignorekeys = new Set(["Backspace", "Delete", "Paste", "Undo", "Cut", "Redo", "Clear", "EraseEof", "Insert"]);

export const formatPhoneNumber = (e: KeyboardEvent) => {
  if (ignorekeys.has(e.key)) {
    return;
  }

  const el = e.target as HTMLInputElement;

  let m = el.value.match(/^\(?(\d{3})\)?$/);
  if (m) {
    const digits = m[1];
    el.value = `(${digits}) `;
  }

  m = el.value.match(/^\(?(\d{3})\)? (\d{3})$/);
  if (m) {
    el.value = `(${m[1]}) ${m[2]}-`;
  }
};

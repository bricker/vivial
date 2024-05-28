import test from "ava";
import { argsToQueryParameters } from "../../src/helpers.mjs";
import "./mock-globals.mjs";

test("argsToQueryParameters converts an object to query params string", (t) => {
  const args = {
    param1: "value1",
    param2: "value2",
    param3: 123,
    param4: true,
  };

  const expectedQueryString = "&param1=value1&param2=value2&param3=123&param4=true";
  const result = argsToQueryParameters(args);

  t.is(result, expectedQueryString);
});

test("argsToQueryParameters handles empty object", (t) => {
  const args = {};

  const expectedQueryString = "";
  const result = argsToQueryParameters(args);

  t.is(result, expectedQueryString);
});

test("argsToQueryParameters handles special characters in values", (t) => {
  const args = {
    param1: "value with spaces",
    param2: "value&with&special&characters",
    param3: "value=with=equal=sign",
  };

  const expectedQueryString =
    "&param1=value%20with%20spaces&param2=value%26with%26special%26characters&param3=value%3Dwith%3Dequal%3Dsign";
  const result = argsToQueryParameters(args);

  t.is(result, expectedQueryString);
});

test("argsToQueryParameters handles special characters in keys", (t) => {
  const args = {
    "special=key": "value",
    "another&special=key": "value",
  };

  const expectedQueryString = "&special%3Dkey=value&another%26special%3Dkey=value";
  const result = argsToQueryParameters(args);

  t.is(result, expectedQueryString);
});

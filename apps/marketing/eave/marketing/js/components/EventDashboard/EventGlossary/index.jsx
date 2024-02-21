// @ts-check
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../../types.js"; // eslint-disable-line no-unused-vars

// TODO: flexbox
const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  menuList: {
    display: "flex",
    flexDirection: "column",
    listStyleType: "none",
    listStyle: "none",
    padding: 0,
    flexGrow: 1,
  },
}));

const EventGlossary = () => {
  return (
    <div>
      <h1>Event Glossary</h1>
    </div>
  );
};

export default EventGlossary;

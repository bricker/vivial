import { makeStyles } from "tss-react/mui";

const stylesTest = makeStyles()(() => ({
  header: {
    fontSize: 24,
    fontWeight: "normal",
    lineHeight: 1.25,
  },
  subHeader: {
    fontSize: 20,
    fontWeight: "normal",
  },
}));

export default stylesTest;

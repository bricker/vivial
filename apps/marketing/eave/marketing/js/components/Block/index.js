import { withStyles } from "@material-ui/styles";
import React from "react";
import Copy from "../Copy/index.jsx";

class Block extends React.Component {
  render() {
    const { classes, copy, img } = this.props;
    return (
      <div className={classes.block}>
        <div className={classes.imageWrapper}>
          <img className={classes.image} src={img.src} alt={img.alt} />
        </div>
        <Copy className={classes.copy} variant="h3">
          {copy}
        </Copy>
      </div>
    );
  }
}

const styles = (theme) => ({
  block: {
    padding: 30,
    marginBottom: 30,
    background: "rgba(255, 255, 255, 0.5)",
    borderRadius: "10px",
    textAlign: "center",
    [theme.breakpoints.up("sm")]: {
      textAlign: "left",
      display: "flex",
      alignItems: "center",
      width: 650,
      padding: "30px 70px",
      marginBottom: 50,
    },
  },
  copy: {
    [theme.breakpoints.up("sm")]: {
      paddingLeft: 70,
      paddingRight: 40,
    },
  },
  imageWrapper: {
    width: 100,
    margin: "0 auto 12px",
    [theme.breakpoints.up("sm")]: {
      width: 135,
      minWidth: 135,
      margin: 0,
    },
  },
  image: {
    width: "100%",
  },
});

export default withStyles(styles)(Block);

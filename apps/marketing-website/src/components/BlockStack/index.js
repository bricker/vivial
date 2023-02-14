import React from 'react';
import { withStyles } from '@material-ui/styles';
import Copy from '../Copy';
import Block from '../Block';

class BlockStack extends React.Component {
  render() {
    const { classes, title, blocks } = this.props;
    return (
      <section className={classes.section}>
        <Copy className={classes.title} variant="h2">
          {title[0]}
          <div>
            {title[1]}
          </div>
        </Copy>
        {blocks.map((block) => (
          <Block
            copy={block.copy}
            img={block.img}
            key={block.copy}
          />
        ))}
      </section>
    );
  }
}

const styles = (theme) => ({
  section: {
    padding: '48px 30px 126px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    [theme.breakpoints.up('sm')]: {
      padding: '100px 100px 180px',
    },
  },
  title: {
    textAlign: 'center',
    marginBottom: 48,
    maxWidth: 275,
    [theme.breakpoints.up('sm')]: {
      maxWidth: 'none',
      marginBottom: 50,
    },
  },
  icon: {
    display: 'inline-block',
    width: 18,
    height: 18,
    [theme.breakpoints.up('sm')]: {
      width: 28,
      height: 28,
    },
  },
});

export default withStyles(styles)(BlockStack);
